from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.sleep_tracker import SleepRecord

router = APIRouter()

class SleepRecordCreate(BaseModel):
    quality: int
    duration: float
    sleep_time: Optional[str] = None  # ISO format, если не указано - вычисляется
    wake_time: Optional[str] = None   # ISO format, если не указано - текущее время
    mood: Optional[str] = None
    notes: Optional[str] = None

class SleepRecordResponse(BaseModel):
    id: str
    quality: int
    duration: float
    sleep_time: str
    wake_time: str
    mood: Optional[str]
    notes: Optional[str]
    created_at: str

    class Config:
        from_attributes = True

class SleepStatsResponse(BaseModel):
    total_records: int
    avg_quality: float
    avg_duration: float
    best_quality: int
    worst_quality: int
    total_sleep_hours: float
    last_7_days_avg_quality: float
    last_7_days_avg_duration: float

@router.post("/records", response_model=SleepRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_sleep_record(
    request: SleepRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Записать сон"""
    
    if not (0 <= request.quality <= 10):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quality must be between 0 and 10"
        )
    
    if request.duration <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duration must be positive"
        )
    
    # Вычислить время если не указано
    now = datetime.utcnow()
    wake_time = datetime.fromisoformat(request.wake_time.replace('Z', '+00:00')) if request.wake_time else now
    sleep_time = datetime.fromisoformat(request.sleep_time.replace('Z', '+00:00')) if request.sleep_time else (wake_time - timedelta(hours=request.duration))
    
    record = SleepRecord(
        user_id=current_user.id,
        quality=request.quality,
        duration=request.duration,
        sleep_time=sleep_time,
        wake_time=wake_time,
        mood=request.mood,
        notes=request.notes
    )
    
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    return SleepRecordResponse(
        id=record.id,
        quality=record.quality,
        duration=record.duration,
        sleep_time=record.sleep_time.isoformat(),
        wake_time=record.wake_time.isoformat(),
        mood=record.mood,
        notes=record.notes,
        created_at=record.created_at.isoformat()
    )

@router.get("/records", response_model=List[SleepRecordResponse])
async def get_sleep_records(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить записи о сне"""
    
    result = await db.execute(
        select(SleepRecord)
        .where(SleepRecord.user_id == current_user.id)
        .order_by(desc(SleepRecord.sleep_time))
        .limit(limit)
    )
    records = result.scalars().all()
    
    return [
        SleepRecordResponse(
            id=r.id,
            quality=r.quality,
            duration=r.duration,
            sleep_time=r.sleep_time.isoformat(),
            wake_time=r.wake_time.isoformat(),
            mood=r.mood,
            notes=r.notes,
            created_at=r.created_at.isoformat()
        )
        for r in records
    ]

@router.get("/stats", response_model=SleepStatsResponse)
async def get_sleep_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику сна"""
    
    # Все записи
    result = await db.execute(
        select(SleepRecord).where(SleepRecord.user_id == current_user.id)
    )
    all_records = result.scalars().all()
    
    if not all_records:
        return SleepStatsResponse(
            total_records=0,
            avg_quality=0,
            avg_duration=0,
            best_quality=0,
            worst_quality=0,
            total_sleep_hours=0,
            last_7_days_avg_quality=0,
            last_7_days_avg_duration=0
        )
    
    # Общая статистика
    total_records = len(all_records)
    avg_quality = sum(r.quality for r in all_records) / total_records
    avg_duration = sum(r.duration for r in all_records) / total_records
    best_quality = max(r.quality for r in all_records)
    worst_quality = min(r.quality for r in all_records)
    total_sleep_hours = sum(r.duration for r in all_records)
    
    # Последние 7 дней
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_records = [r for r in all_records if r.created_at >= seven_days_ago]
    
    if recent_records:
        last_7_days_avg_quality = sum(r.quality for r in recent_records) / len(recent_records)
        last_7_days_avg_duration = sum(r.duration for r in recent_records) / len(recent_records)
    else:
        last_7_days_avg_quality = 0
        last_7_days_avg_duration = 0
    
    return SleepStatsResponse(
        total_records=total_records,
        avg_quality=round(avg_quality, 1),
        avg_duration=round(avg_duration, 1),
        best_quality=best_quality,
        worst_quality=worst_quality,
        total_sleep_hours=round(total_sleep_hours, 1),
        last_7_days_avg_quality=round(last_7_days_avg_quality, 1),
        last_7_days_avg_duration=round(last_7_days_avg_duration, 1)
    )

@router.get("/{record_id}", response_model=SleepRecordResponse)
async def get_sleep_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить запись о сне"""
    
    result = await db.execute(
        select(SleepRecord).where(
            and_(
                SleepRecord.id == record_id,
                SleepRecord.user_id == current_user.id
            )
        )
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sleep record not found"
        )
    
    return SleepRecordResponse(
        id=record.id,
        quality=record.quality,
        duration=record.duration,
        sleep_time=record.sleep_time.isoformat(),
        wake_time=record.wake_time.isoformat(),
        mood=record.mood,
        notes=record.notes,
        created_at=record.created_at.isoformat()
    )

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sleep_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить запись о сне"""
    
    result = await db.execute(
        select(SleepRecord).where(
            and_(
                SleepRecord.id == record_id,
                SleepRecord.user_id == current_user.id
            )
        )
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sleep record not found"
        )
    
    await db.delete(record)
    await db.commit()
