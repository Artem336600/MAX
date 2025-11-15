from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text
from datetime import datetime
import uuid
from core.database import Base

class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(String, nullable=False)  # daily, weekly, monthly
    target_count = Column(Integer, nullable=False, default=1)  # Сколько раз нужно выполнить
    icon = Column(String, nullable=True)  # emoji или icon name
    color = Column(String, nullable=True)  # hex color
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class HabitLog(Base):
    __tablename__ = "habit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id = Column(String, ForeignKey("habits.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
