from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.habit_tracker import Habit, HabitLog

router = APIRouter()

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: str = "daily"
    target_count: int = 1
    icon: Optional[str] = None
    color: Optional[str] = None

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    target_count: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None

class HabitLogCreate(BaseModel):
    notes: Optional[str] = None

class HabitResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    frequency: str
    target_count: int
    icon: Optional[str]
    color: Optional[str]
    active: bool
    created_at: str
    today_count: int = 0
    streak: int = 0

    class Config:
        from_attributes = True

class HabitLogResponse(BaseModel):
    id: str
    habit_id: str
    completed_at: str
    notes: Optional[str]

    class Config:
        from_attributes = True

class HabitStatsResponse(BaseModel):
    total_habits: int
    active_habits: int
    total_completions: int
    completion_rate: float
    best_streak: int

@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    request: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать привычку"""
    
    if request.frequency not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Frequency must be daily, weekly, or monthly"
        )
    
    habit = Habit(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        frequency=request.frequency,
        target_count=request.target_count,
        icon=request.icon,
        color=request.color
    )
    
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    
    return HabitResponse(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        frequency=habit.frequency,
        target_count=habit.target_count,
        icon=habit.icon,
        color=habit.color,
        active=habit.active,
        created_at=habit.created_at.isoformat(),
        today_count=0,
        streak=0
    )

@router.get("", response_model=List[HabitResponse])
async def get_habits(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить привычки"""
    
    query = select(Habit).where(Habit.user_id == current_user.id)
    
    if active_only:
        query = query.where(Habit.active == True)
    
    result = await db.execute(query.order_by(Habit.created_at))
    habits = result.scalars().all()
    
    # Получить логи за сегодня
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    response = []
    for habit in habits:
        # Количество выполнений сегодня
        today_logs_result = await db.execute(
            select(func.count(HabitLog.id))
            .where(
                and_(
                    HabitLog.habit_id == habit.id,
                    HabitLog.completed_at >= today_start
                )
            )
        )
        today_count = today_logs_result.scalar() or 0
        
        # Streak (серия дней подряд)
        streak = await calculate_streak(habit.id, db)
        
        response.append(HabitResponse(
            id=habit.id,
            name=habit.name,
            description=habit.description,
            frequency=habit.frequency,
            target_count=habit.target_count,
            icon=habit.icon,
            color=habit.color,
            active=habit.active,
            created_at=habit.created_at.isoformat(),
            today_count=today_count,
            streak=streak
        ))
    
    return response

async def calculate_streak(habit_id: str, db: AsyncSession) -> int:
    """Вычислить streak (серию дней подряд)"""
    
    # Получить все логи привычки
    result = await db.execute(
        select(HabitLog)
        .where(HabitLog.habit_id == habit_id)
        .order_by(desc(HabitLog.completed_at))
    )
    logs = result.scalars().all()
    
    if not logs:
        return 0
    
    # Проверяем последовательные дни
    streak = 0
    current_date = datetime.utcnow().date()
    
    # Группируем логи по дням
    days_with_logs = set()
    for log in logs:
        days_with_logs.add(log.completed_at.date())
    
    # Считаем streak
    while current_date in days_with_logs:
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak

@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить привычку"""
    
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
                Habit.user_id == current_user.id
            )
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Количество выполнений сегодня
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs_result = await db.execute(
        select(func.count(HabitLog.id))
        .where(
            and_(
                HabitLog.habit_id == habit.id,
                HabitLog.completed_at >= today_start
            )
        )
    )
    today_count = today_logs_result.scalar() or 0
    
    streak = await calculate_streak(habit.id, db)
    
    return HabitResponse(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        frequency=habit.frequency,
        target_count=habit.target_count,
        icon=habit.icon,
        color=habit.color,
        active=habit.active,
        created_at=habit.created_at.isoformat(),
        today_count=today_count,
        streak=streak
    )

@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str,
    request: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить привычку"""
    
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
                Habit.user_id == current_user.id
            )
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Update fields
    if request.name is not None:
        habit.name = request.name
    if request.description is not None:
        habit.description = request.description
    if request.frequency is not None:
        habit.frequency = request.frequency
    if request.target_count is not None:
        habit.target_count = request.target_count
    if request.icon is not None:
        habit.icon = request.icon
    if request.color is not None:
        habit.color = request.color
    if request.active is not None:
        habit.active = request.active
    
    await db.commit()
    await db.refresh(habit)
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs_result = await db.execute(
        select(func.count(HabitLog.id))
        .where(
            and_(
                HabitLog.habit_id == habit.id,
                HabitLog.completed_at >= today_start
            )
        )
    )
    today_count = today_logs_result.scalar() or 0
    streak = await calculate_streak(habit.id, db)
    
    return HabitResponse(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        frequency=habit.frequency,
        target_count=habit.target_count,
        icon=habit.icon,
        color=habit.color,
        active=habit.active,
        created_at=habit.created_at.isoformat(),
        today_count=today_count,
        streak=streak
    )

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить привычку"""
    
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
                Habit.user_id == current_user.id
            )
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Удалить все логи
    logs_result = await db.execute(
        select(HabitLog).where(HabitLog.habit_id == habit_id)
    )
    logs = logs_result.scalars().all()
    for log in logs:
        await db.delete(log)
    
    await db.delete(habit)
    await db.commit()

@router.post("/{habit_id}/complete", response_model=HabitLogResponse, status_code=status.HTTP_201_CREATED)
async def complete_habit(
    habit_id: str,
    request: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отметить выполнение привычки"""
    
    # Проверить что привычка существует
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
                Habit.user_id == current_user.id
            )
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    log = HabitLog(
        habit_id=habit_id,
        notes=request.notes
    )
    
    db.add(log)
    await db.commit()
    await db.refresh(log)
    
    return HabitLogResponse(
        id=log.id,
        habit_id=log.habit_id,
        completed_at=log.completed_at.isoformat(),
        notes=log.notes
    )

@router.get("/{habit_id}/logs", response_model=List[HabitLogResponse])
async def get_habit_logs(
    habit_id: str,
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить логи привычки"""
    
    # Проверить что привычка существует
    result = await db.execute(
        select(Habit).where(
            and_(
                Habit.id == habit_id,
                Habit.user_id == current_user.id
            )
        )
    )
    habit = result.scalar_one_or_none()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    logs_result = await db.execute(
        select(HabitLog)
        .where(HabitLog.habit_id == habit_id)
        .order_by(desc(HabitLog.completed_at))
        .limit(limit)
    )
    logs = logs_result.scalars().all()
    
    return [
        HabitLogResponse(
            id=log.id,
            habit_id=log.habit_id,
            completed_at=log.completed_at.isoformat(),
            notes=log.notes
        )
        for log in logs
    ]

@router.get("/stats/overview", response_model=HabitStatsResponse)
async def get_habits_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить общую статистику привычек"""
    
    # Всего привычек
    total_result = await db.execute(
        select(func.count(Habit.id)).where(Habit.user_id == current_user.id)
    )
    total_habits = total_result.scalar() or 0
    
    # Активных привычек
    active_result = await db.execute(
        select(func.count(Habit.id)).where(
            and_(
                Habit.user_id == current_user.id,
                Habit.active == True
            )
        )
    )
    active_habits = active_result.scalar() or 0
    
    # Всего выполнений
    habits_result = await db.execute(
        select(Habit.id).where(Habit.user_id == current_user.id)
    )
    habit_ids = [row[0] for row in habits_result.all()]
    
    if habit_ids:
        completions_result = await db.execute(
            select(func.count(HabitLog.id)).where(HabitLog.habit_id.in_(habit_ids))
        )
        total_completions = completions_result.scalar() or 0
    else:
        total_completions = 0
    
    # Completion rate (за последние 7 дней)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    if active_habits > 0:
        recent_completions_result = await db.execute(
            select(func.count(HabitLog.id))
            .where(
                and_(
                    HabitLog.habit_id.in_(habit_ids) if habit_ids else False,
                    HabitLog.completed_at >= seven_days_ago
                )
            )
        )
        recent_completions = recent_completions_result.scalar() or 0
        expected_completions = active_habits * 7  # Предполагаем daily habits
        completion_rate = (recent_completions / expected_completions * 100) if expected_completions > 0 else 0
    else:
        completion_rate = 0
    
    # Лучший streak
    best_streak = 0
    for habit_id in habit_ids:
        streak = await calculate_streak(habit_id, db)
        if streak > best_streak:
            best_streak = streak
    
    return HabitStatsResponse(
        total_habits=total_habits,
        active_habits=active_habits,
        total_completions=total_completions,
        completion_rate=round(completion_rate, 1),
        best_streak=best_streak
    )
