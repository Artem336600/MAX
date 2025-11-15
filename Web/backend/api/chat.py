from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.chat import Conversation, Message
from core.ai import ai_engine
from core.module_integration import AIContextBuilder
from core.rag_system import get_rag_system

router = APIRouter()

# Pydantic schemas
class MessageCreate(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    last_message: Optional[str] = None

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    conversation_id: str
    message: MessageResponse

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отправить сообщение в чат"""
    
    # Найти или создать диалог
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Создать новый диалог
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Сохранить сообщение пользователя
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()
    
    # Получить историю сообщений
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    history = result.scalars().all()
    
    # Построить контекст с учётом модулей
    context_builder = AIContextBuilder(db)
    system_prompt = await context_builder.build_system_prompt(
        current_user.id,
        current_user.name
    )
    
    # Добавить глубокий контекст из RAG-системы
    rag = get_rag_system(db)
    rag_context = await rag.get_context_for_ai(current_user.id)
    system_prompt += "\n\n" + rag_context
    
    # Подготовить сообщения для ИИ
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    
    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Получить доступные функции
    available_functions = await context_builder.get_available_functions(current_user.id)
    functions = [f.to_openai_function() for f in available_functions]
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Available functions count: {len(functions)}")
    if functions:
        logger.info(f"First function: {functions[0]}")
    
    # Функция для выполнения вызовов
    async def execute_function(name: str, args: dict):
        logger.info(f"Executing function from chat: {name} with args: {args}")
        return await context_builder.execute_function(name, args, current_user.id)
    
    # Получить ответ от ИИ с поддержкой функций
    try:
        if functions:
            ai_content = await ai_engine.chat_with_functions(
                messages,
                functions,
                execute_function
            )
        else:
            response = await ai_engine.chat(messages)
            ai_content = response.choices[0].message.content
        
        # Сохранить ответ ИИ
        ai_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_content
        )
        db.add(ai_message)
        
        # Обновить время диалога
        conversation.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(ai_message)
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse(
                id=ai_message.id,
                role=ai_message.role,
                content=ai_message.content,
                created_at=ai_message.created_at.isoformat()
            )
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI error: {str(e)}"
        )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список диалогов"""
    
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.updated_at))
    )
    conversations = result.scalars().all()
    
    response = []
    for conv in conversations:
        # Получить последнее сообщение
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()
        
        response.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            last_message=last_msg.content[:100] if last_msg else None
        ))
    
    return response

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить сообщения диалога"""
    
    # Проверить доступ
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Получить сообщения
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить диалог"""
    
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Удалить все сообщения
    await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )
    
    await db.delete(conversation)
    await db.commit()
