from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from datetime import datetime
import uuid
from core.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    priority = Column(String, nullable=False, default="normal")  # low, normal, high, critical
    read = Column(Boolean, default=False, nullable=False)
    module_id = Column(String, ForeignKey("modules.id"), nullable=True)  # Какой модуль отправил
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
