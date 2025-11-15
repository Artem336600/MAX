from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text
import uuid
from core.database import Base

class ModulePage(Base):
    __tablename__ = "module_pages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    module_id = Column(String, ForeignKey("modules.id"), nullable=False)
    title = Column(String, nullable=False)  # Название в меню
    icon = Column(String, nullable=True)  # Emoji или icon name
    path = Column(String, nullable=False)  # URL path, например /sleep-tracker
    component_url = Column(Text, nullable=True)  # URL к React компоненту (для внешних модулей)
    order = Column(Integer, nullable=False, default=0)
    enabled = Column(Boolean, default=True, nullable=False)
