"""
Модели для Schedule Optimizer
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Text, JSON
from sqlalchemy.sql import func
from core.database import Base
import uuid


class DailyReflection(Base):
    """Ежедневная рефлексия пользователя"""
    __tablename__ = "daily_reflections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False)
    
    # Ответы на вопросы
    productivity_score = Column(Integer)  # 1-10
    energy_level = Column(Integer)  # 1-10
    stress_level = Column(Integer)  # 1-10
    mood = Column(String)  # happy, neutral, sad, anxious, etc.
    
    # Что сработало / не сработало
    what_worked = Column(Text)
    what_didnt_work = Column(Text)
    obstacles = Column(Text)
    
    # Задачи
    tasks_completed = Column(Integer, default=0)
    tasks_planned = Column(Integer, default=0)
    
    # Дополнительные заметки
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<DailyReflection {self.date} - User {self.user_id}>"


class ScheduleTemplate(Base):
    """Шаблон расписания"""
    __tablename__ = "schedule_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Настройки шаблона
    config = Column(JSON)  # Гибкая конфигурация
    
    # Статистика использования
    times_used = Column(Integer, default=0)
    avg_success_rate = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)
    is_ai_generated = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ScheduleTemplate {self.name}>"


class TimeBlock(Base):
    """Временной блок в расписании"""
    __tablename__ = "time_blocks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    template_id = Column(String)  # Связь с шаблоном (опционально)
    
    # Время
    date = Column(Date, nullable=False)
    start_time = Column(String, nullable=False)  # HH:MM
    end_time = Column(String, nullable=False)  # HH:MM
    duration_minutes = Column(Integer)
    
    # Тип блока
    block_type = Column(String)  # work, break, focus, meeting, personal, etc.
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Приоритет и энергия
    priority = Column(Integer, default=5)  # 1-10
    required_energy = Column(String)  # high, medium, low
    
    # Результат
    completed = Column(Boolean, default=False)
    actual_duration = Column(Integer)  # Фактическая продолжительность
    effectiveness_score = Column(Integer)  # 1-10
    
    # Метаданные
    tags = Column(JSON)  # Теги для категоризации
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<TimeBlock {self.title} at {self.start_time}>"


class ScheduleInsight(Base):
    """Инсайты и рекомендации по расписанию"""
    __tablename__ = "schedule_insights"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Тип инсайта
    insight_type = Column(String)  # pattern, recommendation, warning, achievement
    category = Column(String)  # productivity, energy, balance, etc.
    
    # Содержание
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Данные для анализа
    data = Column(JSON)
    
    # Приоритет и статус
    priority = Column(String, default="medium")  # low, medium, high
    is_read = Column(Boolean, default=False)
    is_applied = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ScheduleInsight {self.title}>"


class ProductivityMetrics(Base):
    """Метрики продуктивности"""
    __tablename__ = "productivity_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False)
    
    # Основные метрики
    focus_time = Column(Integer, default=0)  # Минуты глубокой работы
    break_time = Column(Integer, default=0)  # Минуты отдыха
    meeting_time = Column(Integer, default=0)  # Минуты встреч
    
    # Эффективность
    planned_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    
    # Энергия и настроение
    avg_energy_level = Column(Float)
    avg_stress_level = Column(Float)
    avg_mood_score = Column(Float)
    
    # Баланс
    work_life_balance_score = Column(Float)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ProductivityMetrics {self.date} - User {self.user_id}>"
