from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text
from datetime import datetime
import uuid
from core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # income, expense
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    limit_amount = Column(Float, nullable=False)
    period = Column(String, nullable=False)  # monthly, weekly, yearly
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
