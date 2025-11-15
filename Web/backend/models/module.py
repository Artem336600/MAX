from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, Boolean, ForeignKey
from datetime import datetime
import uuid
from core.database import Base

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    version = Column(String, nullable=False, default="1.0.0")
    manifest = Column(JSON, nullable=False)  # YAML манифест в JSON
    code = Column(String, nullable=True)  # Python код модуля
    api_key = Column(String, unique=True, nullable=False)  # API ключ модуля
    status = Column(String, nullable=False, default="draft")  # draft, public, private
    rating = Column(Float, default=0.0, nullable=False)
    installs = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UserModule(Base):
    __tablename__ = "user_modules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    module_id = Column(String, ForeignKey("modules.id"), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    config = Column(JSON, nullable=True)  # Конфигурация модуля для пользователя
    installed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
