from sqlalchemy import Column, String, Integer, JSON, ForeignKey
import uuid
from core.database import Base

class Widget(Base):
    __tablename__ = "widgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    module_id = Column(String, ForeignKey("modules.id"), nullable=True)  # Null для встроенных виджетов
    widget_type = Column(String, nullable=False)  # calendar, stats, quick-actions, module-widget
    title = Column(String, nullable=False)
    position_x = Column(Integer, nullable=False, default=0)
    position_y = Column(Integer, nullable=False, default=0)
    width = Column(Integer, nullable=False, default=1)
    height = Column(Integer, nullable=False, default=1)
    config = Column(JSON, nullable=True)  # Конфигурация виджета
    order = Column(Integer, nullable=False, default=0)
