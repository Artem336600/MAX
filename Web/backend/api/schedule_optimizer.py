"""
API для Schedule Optimizer - адаптивное управление расписанием
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, timedelta

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from models.schedule_optimizer import (
    DailyReflection,
    ScheduleTemplate,
    TimeBlock,
    ScheduleInsight,
    ProductivityMetrics
)
from core.rag_system import get_rag_system

router = APIRouter()

# Pydantic schemas
class DailyReflectionCreate(BaseModel):
    productivity_score: int
    energy_level: int
    stress_level: int
    mood: str
    what_worked: Optional[str] = None
    what_didnt_work: Optional[str] = None
    obstacles: Optional[str] = None
    tasks_completed: int = 0
    tasks_planned: int = 0
    notes: Optional[str] = None

class DailyReflectionResponse(BaseModel):
    id: str
    date: str
    productivity_score: int
    energy_level: int
    stress_level: int
    mood: str
    tasks_completed: int
    tasks_planned: int
    
    class Config:
        from_attributes = True

class TimeBlockCreate(BaseModel):
    date: str
    start_time: str
    end_time: str
    block_type: str
    title: str
    description: Optional[str] = None
    priority: int = 5
    required_energy: str = "medium"
    tags: Optional[List[str]] = None

class TimeBlockResponse(BaseModel):
    id: str
    date: str
    start_time: str
    end_time: str
    duration_minutes: Optional[int]
    block_type: str
    title: str
    description: Optional[str]
    priority: int
    completed: bool
    
    class Config:
        from_attributes = True

class DailyQuestionsResponse(BaseModel):
    questions: List[dict]
    context: str

class ScheduleRecommendation(BaseModel):
    title: str
    description: str
    priority: str
    time_blocks: List[dict]


@router.post("/reflection", response_model=DailyReflectionResponse)
async def create_daily_reflection(
    reflection: DailyReflectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать ежедневную рефлексию"""
    
    today = date.today()
    
    # Проверить существующую рефлексию
    existing = await db.execute(
        select(DailyReflection).where(
            and_(
                DailyReflection.user_id == current_user.id,
                DailyReflection.date == today
            )
        )
    )
    existing_reflection = existing.scalar_one_or_none()
    
    if existing_reflection:
        # Обновить существующую
        for key, value in reflection.dict().items():
            setattr(existing_reflection, key, value)
        
        await db.commit()
        await db.refresh(existing_reflection)
        
        return DailyReflectionResponse(
            id=existing_reflection.id,
            date=existing_reflection.date.isoformat(),
            productivity_score=existing_reflection.productivity_score,
            energy_level=existing_reflection.energy_level,
            stress_level=existing_reflection.stress_level,
            mood=existing_reflection.mood,
            tasks_completed=existing_reflection.tasks_completed,
            tasks_planned=existing_reflection.tasks_planned
        )
    
    # Создать новую
    new_reflection = DailyReflection(
        user_id=current_user.id,
        date=today,
        **reflection.dict()
    )
    
    db.add(new_reflection)
    await db.commit()
    await db.refresh(new_reflection)
    
    # Обновить метрики продуктивности
    await _update_productivity_metrics(db, current_user.id, today, new_reflection)
    
    # Сгенерировать инсайты на основе рефлексии
    await _generate_insights_from_reflection(db, current_user.id, new_reflection)
    
    return DailyReflectionResponse(
        id=new_reflection.id,
        date=new_reflection.date.isoformat(),
        productivity_score=new_reflection.productivity_score,
        energy_level=new_reflection.energy_level,
        stress_level=new_reflection.stress_level,
        mood=new_reflection.mood,
        tasks_completed=new_reflection.tasks_completed,
        tasks_planned=new_reflection.tasks_planned
    )


@router.get("/daily-questions", response_model=DailyQuestionsResponse)
async def get_daily_questions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить ежедневные вопросы с учетом контекста пользователя"""
    
    # Получить контекст из RAG-системы
    rag = get_rag_system(db)
    context = await rag.build_user_context(current_user.id)
    
    # Базовые вопросы
    questions = [
        {
            "id": "productivity",
            "question": "Как ты оцениваешь свою продуктивность сегодня?",
            "type": "scale",
            "min": 1,
            "max": 10,
            "field": "productivity_score"
        },
        {
            "id": "energy",
            "question": "Какой был твой уровень энергии?",
            "type": "scale",
            "min": 1,
            "max": 10,
            "field": "energy_level"
        },
        {
            "id": "stress",
            "question": "Насколько стрессовым был день?",
            "type": "scale",
            "min": 1,
            "max": 10,
            "field": "stress_level"
        },
        {
            "id": "mood",
            "question": "Как ты себя чувствуешь?",
            "type": "choice",
            "options": ["Отлично", "Хорошо", "Нормально", "Плохо", "Ужасно"],
            "field": "mood"
        },
        {
            "id": "tasks",
            "question": "Сколько задач ты выполнил из запланированных?",
            "type": "number",
            "field": "tasks_completed"
        }
    ]
    
    # Адаптивные вопросы на основе паттернов
    patterns = context.patterns
    
    # Если есть проблемы со сном
    sleep_pattern = patterns.get("sleep_pattern", {})
    if sleep_pattern.get("status") == "needs_improvement":
        questions.append({
            "id": "sleep_quality",
            "question": "Как ты спал прошлой ночью?",
            "type": "choice",
            "options": ["Отлично", "Хорошо", "Плохо", "Очень плохо"],
            "field": "notes"
        })
    
    # Если низкая продуктивность
    productivity = patterns.get("productivity_pattern", {})
    if productivity.get("status") == "low":
        questions.append({
            "id": "obstacles",
            "question": "Что мешало тебе быть продуктивным сегодня?",
            "type": "text",
            "field": "obstacles"
        })
    
    # Контекст для ИИ
    context_text = f"""
Пользователь: {current_user.name}

Текущие паттерны:
- Сон: {sleep_pattern.get('status', 'нет данных')}
- Продуктивность: {productivity.get('status', 'нет данных')}

Активные инсайты: {len(context.insights)}
"""
    
    return DailyQuestionsResponse(
        questions=questions,
        context=context_text
    )


@router.get("/recommendations", response_model=List[ScheduleRecommendation])
async def get_schedule_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить рекомендации по оптимизации расписания"""
    
    # Получить контекст пользователя
    rag = get_rag_system(db)
    context = await rag.build_user_context(current_user.id)
    
    recommendations = []
    
    # Рекомендация на основе паттерна сна
    sleep_pattern = context.patterns.get("sleep_pattern", {})
    if sleep_pattern.get("status") == "needs_improvement":
        recommendations.append(ScheduleRecommendation(
            title="Улучши качество сна",
            description=sleep_pattern.get("recommendation", ""),
            priority="high",
            time_blocks=[
                {
                    "start_time": "22:30",
                    "end_time": "23:00",
                    "title": "Подготовка ко сну",
                    "block_type": "personal",
                    "description": "Отключи гаджеты, почитай книгу"
                }
            ]
        ))
    
    # Рекомендация на основе продуктивности
    productivity = context.patterns.get("productivity_pattern", {})
    if productivity.get("status") == "low":
        recommendations.append(ScheduleRecommendation(
            title="Структурируй рабочее время",
            description="Используй технику Pomodoro для повышения фокуса",
            priority="high",
            time_blocks=[
                {
                    "start_time": "09:00",
                    "end_time": "09:25",
                    "title": "Фокус-сессия 1",
                    "block_type": "focus",
                    "description": "25 минут глубокой работы"
                },
                {
                    "start_time": "09:25",
                    "end_time": "09:30",
                    "title": "Короткий перерыв",
                    "block_type": "break",
                    "description": "5 минут отдыха"
                }
            ]
        ))
    
    # Рекомендация по балансу
    time_mgmt = context.patterns.get("time_management", {})
    if time_mgmt.get("balance") == "needs_adjustment":
        recommendations.append(ScheduleRecommendation(
            title="Улучши work-life баланс",
            description=time_mgmt.get("recommendation", ""),
            priority="medium",
            time_blocks=[
                {
                    "start_time": "18:00",
                    "end_time": "19:00",
                    "title": "Личное время",
                    "block_type": "personal",
                    "description": "Спорт, хобби или время с семьей"
                }
            ]
        ))
    
    return recommendations


@router.post("/time-blocks", response_model=TimeBlockResponse)
async def create_time_block(
    block: TimeBlockCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать временной блок"""
    
    # Рассчитать продолжительность
    start = datetime.strptime(block.start_time, "%H:%M")
    end = datetime.strptime(block.end_time, "%H:%M")
    duration = int((end - start).total_seconds() / 60)
    
    new_block = TimeBlock(
        user_id=current_user.id,
        date=datetime.fromisoformat(block.date).date(),
        start_time=block.start_time,
        end_time=block.end_time,
        duration_minutes=duration,
        block_type=block.block_type,
        title=block.title,
        description=block.description,
        priority=block.priority,
        required_energy=block.required_energy,
        tags=block.tags
    )
    
    db.add(new_block)
    await db.commit()
    await db.refresh(new_block)
    
    return TimeBlockResponse(
        id=new_block.id,
        date=new_block.date.isoformat(),
        start_time=new_block.start_time,
        end_time=new_block.end_time,
        duration_minutes=new_block.duration_minutes,
        block_type=new_block.block_type,
        title=new_block.title,
        description=new_block.description,
        priority=new_block.priority,
        completed=new_block.completed
    )


@router.get("/time-blocks", response_model=List[TimeBlockResponse])
async def get_time_blocks(
    date_str: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить временные блоки"""
    
    target_date = datetime.fromisoformat(date_str).date() if date_str else date.today()
    
    result = await db.execute(
        select(TimeBlock)
        .where(
            and_(
                TimeBlock.user_id == current_user.id,
                TimeBlock.date == target_date
            )
        )
        .order_by(TimeBlock.start_time)
    )
    
    blocks = result.scalars().all()
    
    return [
        TimeBlockResponse(
            id=block.id,
            date=block.date.isoformat(),
            start_time=block.start_time,
            end_time=block.end_time,
            duration_minutes=block.duration_minutes,
            block_type=block.block_type,
            title=block.title,
            description=block.description,
            priority=block.priority,
            completed=block.completed
        )
        for block in blocks
    ]


@router.get("/insights", response_model=List[dict])
async def get_schedule_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить инсайты по расписанию"""
    
    result = await db.execute(
        select(ScheduleInsight)
        .where(ScheduleInsight.user_id == current_user.id)
        .order_by(desc(ScheduleInsight.created_at))
        .limit(10)
    )
    
    insights = result.scalars().all()
    
    return [
        {
            "id": insight.id,
            "type": insight.insight_type,
            "category": insight.category,
            "title": insight.title,
            "description": insight.description,
            "priority": insight.priority,
            "is_read": insight.is_read,
            "created_at": insight.created_at.isoformat()
        }
        for insight in insights
    ]


async def _update_productivity_metrics(
    db: AsyncSession,
    user_id: str,
    target_date: date,
    reflection: DailyReflection
):
    """Обновить метрики продуктивности"""
    
    # Проверить существующие метрики
    result = await db.execute(
        select(ProductivityMetrics).where(
            and_(
                ProductivityMetrics.user_id == user_id,
                ProductivityMetrics.date == target_date
            )
        )
    )
    metrics = result.scalar_one_or_none()
    
    completion_rate = (
        reflection.tasks_completed / reflection.tasks_planned
        if reflection.tasks_planned > 0 else 0
    )
    
    if metrics:
        # Обновить
        metrics.planned_tasks = reflection.tasks_planned
        metrics.completed_tasks = reflection.tasks_completed
        metrics.completion_rate = completion_rate
        metrics.avg_energy_level = reflection.energy_level
        metrics.avg_stress_level = reflection.stress_level
    else:
        # Создать новые
        metrics = ProductivityMetrics(
            user_id=user_id,
            date=target_date,
            planned_tasks=reflection.tasks_planned,
            completed_tasks=reflection.tasks_completed,
            completion_rate=completion_rate,
            avg_energy_level=reflection.energy_level,
            avg_stress_level=reflection.stress_level
        )
        db.add(metrics)
    
    await db.commit()


async def _generate_insights_from_reflection(
    db: AsyncSession,
    user_id: str,
    reflection: DailyReflection
):
    """Сгенерировать инсайты на основе рефлексии"""
    
    insights_to_create = []
    
    # Низкая продуктивность
    if reflection.productivity_score < 4:
        insights_to_create.append(ScheduleInsight(
            user_id=user_id,
            insight_type="warning",
            category="productivity",
            title="Низкая продуктивность",
            description=f"Сегодня продуктивность была {reflection.productivity_score}/10. "
                       f"Что помешало? {reflection.obstacles or 'Не указано'}",
            priority="high"
        ))
    
    # Высокий стресс
    if reflection.stress_level > 7:
        insights_to_create.append(ScheduleInsight(
            user_id=user_id,
            insight_type="warning",
            category="wellbeing",
            title="Высокий уровень стресса",
            description="Стоит добавить больше времени на отдых и восстановление",
            priority="high"
        ))
    
    # Низкая энергия
    if reflection.energy_level < 4:
        insights_to_create.append(ScheduleInsight(
            user_id=user_id,
            insight_type="recommendation",
            category="energy",
            title="Низкий уровень энергии",
            description="Проверь качество сна и добавь физическую активность",
            priority="medium"
        ))
    
    # Добавить инсайты
    for insight in insights_to_create:
        db.add(insight)
    
    await db.commit()
