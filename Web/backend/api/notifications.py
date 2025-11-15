from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.notification import Notification

router = APIRouter()

class NotificationCreate(BaseModel):
    title: str
    message: str
    priority: str = "normal"
    module_id: Optional[str] = None

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    priority: str
    read: bool
    module_id: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить уведомления пользователя"""
    
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.read == False)
    
    query = query.order_by(desc(Notification.created_at))
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return [
        NotificationResponse(
            id=n.id,
            title=n.title,
            message=n.message,
            priority=n.priority,
            read=n.read,
            module_id=n.module_id,
            created_at=n.created_at.isoformat()
        )
        for n in notifications
    ]

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    request: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать уведомление"""
    
    notification = Notification(
        user_id=current_user.id,
        title=request.title,
        message=request.message,
        priority=request.priority,
        module_id=request.module_id
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return NotificationResponse(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        priority=notification.priority,
        read=notification.read,
        module_id=notification.module_id,
        created_at=notification.created_at.isoformat()
    )

@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отметить уведомление как прочитанное"""
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.read = True
    await db.commit()
    
    return {"success": True}

@router.put("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отметить все уведомления как прочитанные"""
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.read == False
            )
        )
    )
    notifications = result.scalars().all()
    
    for notification in notifications:
        notification.read = True
    
    await db.commit()
    
    return {"success": True, "count": len(notifications)}

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить уведомление"""
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    await db.delete(notification)
    await db.commit()

@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить количество непрочитанных уведомлений"""
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.read == False
            )
        )
    )
    count = len(result.scalars().all())
    
    return {"count": count}
