from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.calendar import CalendarEvent

router = APIRouter()

# Pydantic schemas
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    all_day: bool = False
    recurrence: Optional[str] = None
    reminder_minutes: Optional[int] = None
    color: str = "#3B82F6"

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    recurrence: Optional[str] = None
    reminder_minutes: Optional[int] = None
    color: Optional[str] = None

class EventResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    start_time: str
    end_time: Optional[str]
    all_day: bool
    recurrence: Optional[str]
    reminder_minutes: Optional[int]
    color: str
    module_id: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: EventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать событие в календаре"""
    
    event = CalendarEvent(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time,
        all_day=request.all_day,
        recurrence=request.recurrence,
        reminder_minutes=request.reminder_minutes,
        color=request.color
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat() if event.end_time else None,
        all_day=event.all_day,
        recurrence=event.recurrence,
        reminder_minutes=event.reminder_minutes,
        color=event.color,
        module_id=event.module_id,
        created_at=event.created_at.isoformat()
    )

@router.get("", response_model=List[EventResponse])
async def get_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить события пользователя"""
    
    query = select(CalendarEvent).where(CalendarEvent.user_id == current_user.id)
    
    # Фильтрация по датам
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.where(CalendarEvent.start_time >= start_dt)
    
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.where(CalendarEvent.start_time <= end_dt)
    
    query = query.order_by(CalendarEvent.start_time)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return [
        EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            start_time=event.start_time.isoformat(),
            end_time=event.end_time.isoformat() if event.end_time else None,
            all_day=event.all_day,
            recurrence=event.recurrence,
            reminder_minutes=event.reminder_minutes,
            color=event.color,
            module_id=event.module_id,
            created_at=event.created_at.isoformat()
        )
        for event in events
    ]

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить событие по ID"""
    
    result = await db.execute(
        select(CalendarEvent).where(
            and_(
                CalendarEvent.id == event_id,
                CalendarEvent.user_id == current_user.id
            )
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat() if event.end_time else None,
        all_day=event.all_day,
        recurrence=event.recurrence,
        reminder_minutes=event.reminder_minutes,
        color=event.color,
        module_id=event.module_id,
        created_at=event.created_at.isoformat()
    )

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    request: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить событие"""
    
    result = await db.execute(
        select(CalendarEvent).where(
            and_(
                CalendarEvent.id == event_id,
                CalendarEvent.user_id == current_user.id
            )
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Update fields
    if request.title is not None:
        event.title = request.title
    if request.description is not None:
        event.description = request.description
    if request.start_time is not None:
        event.start_time = request.start_time
    if request.end_time is not None:
        event.end_time = request.end_time
    if request.all_day is not None:
        event.all_day = request.all_day
    if request.recurrence is not None:
        event.recurrence = request.recurrence
    if request.reminder_minutes is not None:
        event.reminder_minutes = request.reminder_minutes
    if request.color is not None:
        event.color = request.color
    
    event.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(event)
    
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time.isoformat(),
        end_time=event.end_time.isoformat() if event.end_time else None,
        all_day=event.all_day,
        recurrence=event.recurrence,
        reminder_minutes=event.reminder_minutes,
        color=event.color,
        module_id=event.module_id,
        created_at=event.created_at.isoformat()
    )

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить событие"""
    
    result = await db.execute(
        select(CalendarEvent).where(
            and_(
                CalendarEvent.id == event_id,
                CalendarEvent.user_id == current_user.id
            )
        )
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    await db.delete(event)
    await db.commit()
