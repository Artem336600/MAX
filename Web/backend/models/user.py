from sqlalchemy import Column, String, DateTime, Enum, Integer
from datetime import datetime
import uuid
import enum
from core.database import Base

class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    maks_id = Column(Integer, nullable=True)  # ID в MAKS (уникальность через индекс в БД)
    maks_username = Column(String, nullable=True)  # Логин для входа (уникальность через индекс в БД)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
