from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.widget import Widget

router = APIRouter()

class WidgetCreate(BaseModel):
    module_id: Optional[str] = None
    widget_type: str
    title: str
    position_x: int = 0
    position_y: int = 0
    width: int = 1
    height: int = 1
    config: Optional[Dict[str, Any]] = None

class WidgetUpdate(BaseModel):
    title: Optional[str] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    order: Optional[int] = None

class WidgetResponse(BaseModel):
    id: str
    module_id: Optional[str]
    widget_type: str
    title: str
    position_x: int
    position_y: int
    width: int
    height: int
    config: Optional[Dict[str, Any]]
    order: int

    class Config:
        from_attributes = True

@router.get("", response_model=List[WidgetResponse])
async def get_widgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить виджеты пользователя"""
    
    result = await db.execute(
        select(Widget)
        .where(Widget.user_id == current_user.id)
        .order_by(Widget.order)
    )
    widgets = result.scalars().all()
    
    return [
        WidgetResponse(
            id=w.id,
            module_id=w.module_id,
            widget_type=w.widget_type,
            title=w.title,
            position_x=w.position_x,
            position_y=w.position_y,
            width=w.width,
            height=w.height,
            config=w.config,
            order=w.order
        )
        for w in widgets
    ]

@router.post("", response_model=WidgetResponse, status_code=status.HTTP_201_CREATED)
async def create_widget(
    request: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать виджет"""
    
    # Получить максимальный order
    result = await db.execute(
        select(Widget)
        .where(Widget.user_id == current_user.id)
        .order_by(Widget.order.desc())
    )
    last_widget = result.scalars().first()
    next_order = (last_widget.order + 1) if last_widget else 0
    
    widget = Widget(
        user_id=current_user.id,
        module_id=request.module_id,
        widget_type=request.widget_type,
        title=request.title,
        position_x=request.position_x,
        position_y=request.position_y,
        width=request.width,
        height=request.height,
        config=request.config,
        order=next_order
    )
    
    db.add(widget)
    await db.commit()
    await db.refresh(widget)
    
    return WidgetResponse(
        id=widget.id,
        module_id=widget.module_id,
        widget_type=widget.widget_type,
        title=widget.title,
        position_x=widget.position_x,
        position_y=widget.position_y,
        width=widget.width,
        height=widget.height,
        config=widget.config,
        order=widget.order
    )

@router.put("/{widget_id}", response_model=WidgetResponse)
async def update_widget(
    widget_id: str,
    request: WidgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить виджет"""
    
    result = await db.execute(
        select(Widget).where(
            and_(
                Widget.id == widget_id,
                Widget.user_id == current_user.id
            )
        )
    )
    widget = result.scalar_one_or_none()
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found"
        )
    
    # Update fields
    if request.title is not None:
        widget.title = request.title
    if request.position_x is not None:
        widget.position_x = request.position_x
    if request.position_y is not None:
        widget.position_y = request.position_y
    if request.width is not None:
        widget.width = request.width
    if request.height is not None:
        widget.height = request.height
    if request.config is not None:
        widget.config = request.config
    if request.order is not None:
        widget.order = request.order
    
    await db.commit()
    await db.refresh(widget)
    
    return WidgetResponse(
        id=widget.id,
        module_id=widget.module_id,
        widget_type=widget.widget_type,
        title=widget.title,
        position_x=widget.position_x,
        position_y=widget.position_y,
        width=widget.width,
        height=widget.height,
        config=widget.config,
        order=widget.order
    )

@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить виджет"""
    
    result = await db.execute(
        select(Widget).where(
            and_(
                Widget.id == widget_id,
                Widget.user_id == current_user.id
            )
        )
    )
    widget = result.scalar_one_or_none()
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found"
        )
    
    await db.delete(widget)
    await db.commit()

@router.post("/reset")
async def reset_widgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Сбросить виджеты к дефолтным"""
    
    # Удалить все виджеты
    result = await db.execute(
        select(Widget).where(Widget.user_id == current_user.id)
    )
    widgets = result.scalars().all()
    
    for widget in widgets:
        await db.delete(widget)
    
    # Создать дефолтные виджеты
    default_widgets = [
        Widget(
            user_id=current_user.id,
            widget_type="calendar",
            title="Календарь",
            position_x=0,
            position_y=0,
            width=2,
            height=2,
            order=0
        ),
        Widget(
            user_id=current_user.id,
            widget_type="quick-actions",
            title="Быстрые действия",
            position_x=2,
            position_y=0,
            width=1,
            height=1,
            order=1
        ),
        Widget(
            user_id=current_user.id,
            widget_type="stats",
            title="Статистика",
            position_x=2,
            position_y=1,
            width=1,
            height=1,
            order=2
        )
    ]
    
    for widget in default_widgets:
        db.add(widget)
    
    await db.commit()
    
    return {"success": True, "message": "Widgets reset to default"}
