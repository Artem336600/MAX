from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from datetime import datetime
import uuid
from core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="Новый диалог")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    function_call = Column(JSON, nullable=True)  # Для function calling
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
