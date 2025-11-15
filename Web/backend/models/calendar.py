from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from datetime import datetime
import uuid
from core.database import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    all_day = Column(Boolean, default=False, nullable=False)
    recurrence = Column(String, nullable=True)  # daily, weekly, monthly, yearly
    reminder_minutes = Column(Integer, nullable=True)  # Напоминание за N минут
    color = Column(String, default="#3B82F6", nullable=False)  # Цвет события
    module_id = Column(String, nullable=True)  # Какой модуль создал событие
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
