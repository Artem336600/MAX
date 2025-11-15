from sqlalchemy import Column, String, DateTime, Float, Integer, Text, ForeignKey
from datetime import datetime
import uuid
from core.database import Base

class SleepRecord(Base):
    __tablename__ = "sleep_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    quality = Column(Integer, nullable=False)  # 0-10
    duration = Column(Float, nullable=False)  # часы
    sleep_time = Column(DateTime, nullable=False)
    wake_time = Column(DateTime, nullable=False)
    mood = Column(String, nullable=True)  # great, good, normal, bad, terrible
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
