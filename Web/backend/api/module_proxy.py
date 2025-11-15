"""
Proxy для вызова внешних модулей
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Dict, Any, Optional
import aiohttp

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.module import Module

router = APIRouter()

class ModuleCallRequest(BaseModel):
    endpoint: str
    method: str = "POST"
    data: Optional[Dict[str, Any]] = None

class ModuleCallResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None

@router.post("/{module_id}/call", response_model=ModuleCallResponse)
async def call_external_module(
    module_id: str,
    request: ModuleCallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Вызвать внешний модуль
    
    Модуль должен быть запущен локально и слушать на указанном URL
    """
    
    # Получить модуль
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Получить URL модуля из манифеста
    manifest = module.manifest or {}
    module_url = manifest.get('webhook_url')
    
    if not module_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module does not have webhook_url configured"
        )
    
    # Подготовить данные для модуля
    payload = {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "user_name": current_user.name,
        "endpoint": request.endpoint,
        "data": request.data or {}
    }
    
    # Вызвать модуль
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "X-Eidos-Module-Key": module.api_key,
                "Content-Type": "application/json"
            }
            
            # Убедимся что URL правильный
            if not request.endpoint.startswith('/'):
                url = f"{module_url}/{request.endpoint}"
            else:
                url = f"{module_url}{request.endpoint}"
            
            async with session.request(
                request.method,
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    return ModuleCallResponse(
                        success=False,
                        data=None,
                        error=f"Module returned error: {error_text}"
                    )
                
                data = await response.json()
                return ModuleCallResponse(
                    success=True,
                    data=data,
                    error=None
                )
    
    except aiohttp.ClientError as e:
        return ModuleCallResponse(
            success=False,
            data=None,
            error=f"Failed to connect to module: {str(e)}"
        )
    except Exception as e:
        return ModuleCallResponse(
            success=False,
            data=None,
            error=f"Unexpected error: {str(e)}"
        )

@router.post("/webhook/{module_api_key}")
async def module_webhook(
    module_api_key: str,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook для обратных вызовов от модулей
    
    Модули могут вызывать этот endpoint для отправки уведомлений,
    создания событий и т.д.
    """
    
    # Найти модуль по API ключу
    result = await db.execute(
        select(Module).where(Module.api_key == module_api_key)
    )
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid module API key"
        )
    
    # Обработать запрос от модуля
    action = data.get('action')
    
    if action == 'notify':
        # Отправить уведомление пользователю
        # TODO: реализовать систему уведомлений
        return {"success": True, "message": "Notification sent"}
    
    elif action == 'create_event':
        # Создать событие в календаре
        # TODO: вызвать calendar API
        return {"success": True, "message": "Event created"}
    
    elif action == 'store_data':
        # Сохранить данные модуля
        # TODO: реализовать хранилище данных модулей
        return {"success": True, "message": "Data stored"}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown action: {action}"
        )
