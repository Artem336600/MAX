"""
Упрощенная интеграция с Web Backend (без зависимости от config)
"""

import sys
import os

# Добавить путь к Web backend
web_backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Web/backend'))
sys.path.insert(0, web_backend_path)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Импорт моделей напрямую (без config)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text

Base = declarative_base()

# Определяем модели локально чтобы избежать импорта config
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    maks_id = Column(Integer, nullable=True)  # ID в MAKS (уникальность через индекс)
    maks_username = Column(String, nullable=True)  # Логин для сайта (уникальность через индекс)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SleepRecord(Base):
    __tablename__ = "sleep_records"
    
    id = Column(String, primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = Column(String, nullable=False)
    quality = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    sleep_time = Column(DateTime, nullable=False)
    wake_time = Column(DateTime, nullable=False)
    mood = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(String, primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    frequency = Column(String, nullable=False)
    target_count = Column(Integer, default=1)
    icon = Column(String, default="⭐")
    color = Column(String, default="#6366F1")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class HabitLog(Base):
    __tablename__ = "habit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    habit_id = Column(String, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = Column(String, nullable=False)
    type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class WebBackendIntegration:
    """Упрощенная интеграция с Web Backend"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Путь к БД Web по умолчанию
            db_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                '../../Web/backend/eidos.db'
            ))
        
        db_url = f"sqlite+aiosqlite:///{db_path}"
        
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info(f"Connected to Web DB: {db_url}")
    
    async def get_or_create_user(self, maks_id: int, name: str, generate_credentials: bool = False) -> tuple[User, Optional[str]]:
        """
        Получить или создать пользователя
        
        Returns:
            (User, password) - пользователь и пароль (если создан новый)
        """
        async with self.async_session() as session:
            # Ищем по maks_id
            result = await session.execute(
                select(User).where(User.maks_id == maks_id)
            )
            user = result.scalar_one_or_none()
            
            # Если не нашли по maks_id, ищем по email (для старых пользователей)
            if not user:
                email = f"maks_{maks_id}@bot.local"
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()
                
                # Если нашли по email - обновляем maks_id и username
                if user:
                    import sys
                    import os
                    
                    # Добавить путь к utils
                    utils_path = os.path.join(os.path.dirname(__file__), '..')
                    if utils_path not in sys.path:
                        sys.path.insert(0, utils_path)
                    
                    from utils.credentials import generate_username
                    
                    user.maks_id = maks_id
                    user.maks_username = generate_username(maks_id)
                    await session.commit()
                    await session.refresh(user)
                    logger.info(f"Updated existing user with MAKS ID {maks_id}")
                    return user, None
            
            if not user:
                import uuid
                import hashlib
                import sys
                import os
                
                # Добавить путь к utils
                utils_path = os.path.join(os.path.dirname(__file__), '..')
                if utils_path not in sys.path:
                    sys.path.insert(0, utils_path)
                
                # Генерируем учетные данные
                from utils.credentials import generate_username, generate_simple_password, hash_password
                
                username = generate_username(maks_id)
                password = generate_simple_password(8)
                
                user = User(
                    id=str(uuid.uuid4()),
                    email=f"maks_{maks_id}@bot.local",
                    name=name,
                    password_hash=hash_password(password),
                    role="user",
                    maks_id=maks_id,
                    maks_username=username
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"Created new user for MAKS ID {maks_id}: {username}")
                
                return user, password
            
            return user, None
    
    async def create_sleep_record(self, user_id: str, quality: int, duration: float, **kwargs) -> SleepRecord:
        """Создать запись о сне"""
        async with self.async_session() as session:
            import uuid
            now = datetime.utcnow()
            
            sleep_time = kwargs.get('sleep_time')
            wake_time = kwargs.get('wake_time')
            
            if wake_time:
                wake_dt = datetime.fromisoformat(wake_time.replace('Z', '+00:00'))
            else:
                wake_dt = now
            
            if sleep_time:
                sleep_dt = datetime.fromisoformat(sleep_time.replace('Z', '+00:00'))
            else:
                sleep_dt = wake_dt - timedelta(hours=duration)
            
            record = SleepRecord(
                id=str(uuid.uuid4()),
                user_id=user_id,
                quality=quality,
                duration=duration,
                sleep_time=sleep_dt,
                wake_time=wake_dt,
                mood=kwargs.get('mood'),
                notes=kwargs.get('notes')
            )
            
            session.add(record)
            await session.commit()
            await session.refresh(record)
            
            return record
    
    async def get_sleep_stats(self, user_id: str) -> Dict[str, Any]:
        """Получить статистику сна"""
        async with self.async_session() as session:
            result = await session.execute(
                select(SleepRecord).where(SleepRecord.user_id == user_id)
            )
            records = result.scalars().all()
            
            if not records:
                return {"total_records": 0, "avg_quality": 0, "avg_duration": 0}
            
            return {
                "total_records": len(records),
                "avg_quality": round(sum(r.quality for r in records) / len(records), 1),
                "avg_duration": round(sum(r.duration for r in records) / len(records), 1),
                "best_quality": max(r.quality for r in records),
                "worst_quality": min(r.quality for r in records)
            }
    
    async def create_habit(self, user_id: str, name: str, frequency: str, **kwargs) -> Habit:
        """Создать привычку"""
        async with self.async_session() as session:
            import uuid
            habit = Habit(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=name,
                description=kwargs.get('description', ''),
                frequency=frequency,
                icon=kwargs.get('icon', '⭐'),
                color="#6366F1",
                active=True
            )
            
            session.add(habit)
            await session.commit()
            await session.refresh(habit)
            
            return habit
    
    async def get_habits(self, user_id: str):
        """Получить список привычек"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Habit).where(Habit.user_id == user_id, Habit.active == True)
            )
            return result.scalars().all()
    
    async def log_habit(self, habit_id: str, notes: Optional[str] = None) -> HabitLog:
        """Отметить выполнение привычки"""
        async with self.async_session() as session:
            import uuid
            log = HabitLog(
                id=str(uuid.uuid4()),
                habit_id=habit_id,
                completed_at=datetime.utcnow(),
                notes=notes
            )
            
            session.add(log)
            await session.commit()
            await session.refresh(log)
            
            return log
    
    async def create_transaction(self, user_id: str, type: str, amount: float, category: str, **kwargs) -> Transaction:
        """Создать транзакцию"""
        async with self.async_session() as session:
            import uuid
            date_str = kwargs.get('date')
            
            transaction = Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                type=type,
                amount=amount,
                category=category,
                description=kwargs.get('description', ''),
                date=datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else datetime.utcnow()
            )
            
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            
            return transaction
    
    async def get_finance_stats(self, user_id: str) -> Dict[str, Any]:
        """Получить финансовую статистику"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Transaction).where(Transaction.user_id == user_id)
            )
            transactions = result.scalars().all()
            
            income = sum(t.amount for t in transactions if t.type == 'income')
            expense = sum(t.amount for t in transactions if t.type == 'expense')
            
            return {
                "balance": income - expense,
                "total_income": income,
                "total_expense": expense,
                "transactions_count": len(transactions)
            }
    
    async def execute_function(self, function_name: str, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Выполнить функцию модуля"""
        try:
            if function_name == "create_sleep_record":
                record = await self.create_sleep_record(user_id=user_id, **arguments)
                return {"success": True, "data": {"id": record.id, "quality": record.quality, "duration": record.duration}}
            
            elif function_name == "get_sleep_stats":
                stats = await self.get_sleep_stats(user_id)
                return {"success": True, "data": stats}
            
            elif function_name == "create_habit":
                habit = await self.create_habit(user_id=user_id, **arguments)
                return {"success": True, "data": {"id": habit.id, "name": habit.name, "frequency": habit.frequency}}
            
            elif function_name == "get_habits":
                habits = await self.get_habits(user_id)
                return {"success": True, "data": [{"id": h.id, "name": h.name, "frequency": h.frequency} for h in habits]}
            
            elif function_name == "log_habit":
                log = await self.log_habit(**arguments)
                return {"success": True, "data": {"id": log.id}}
            
            elif function_name == "create_transaction":
                transaction = await self.create_transaction(user_id=user_id, **arguments)
                return {"success": True, "data": {"id": transaction.id, "type": transaction.type, "amount": transaction.amount}}
            
            elif function_name == "get_finance_stats":
                stats = await self.get_finance_stats(user_id)
                return {"success": True, "data": stats}
            
            elif function_name == "create_calendar_event":
                # Создать событие в календаре через HTTP API
                import httpx
                from datetime import datetime, timedelta
                import jwt
                import os
                
                # Создать JWT токен локально (используем тот же SECRET_KEY что и backend)
                SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
                to_encode = {"sub": user_id}
                expire = datetime.utcnow() + timedelta(hours=24)
                to_encode.update({"exp": expire})
                token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
                
                logger.info(f"Created JWT token for user {user_id}")
                
                # Подготовить данные
                event_data = {
                    "title": arguments.get("title"),
                    "start_time": arguments.get("start_time"),
                    "end_time": arguments.get("end_time"),
                    "description": arguments.get("description"),
                    "reminder_minutes": arguments.get("reminder_minutes"),
                    "all_day": False
                }
                
                # Отправить запрос на backend
                logger.info(f"Creating calendar event for user {user_id}: {event_data}")
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://localhost:8001/api/v1/calendar/events",
                        json=event_data,
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    
                    logger.info(f"Calendar API response: {response.status_code}")
                    if response.status_code in [200, 201]:
                        result = response.json()
                        logger.info(f"Event created successfully: {result}")
                        return {"success": True, "data": result}
                    else:
                        logger.error(f"Calendar API error: {response.status_code} - {response.text}")
                        return {"success": False, "error": f"API error: {response.status_code} - {response.text}"}
            
            elif function_name == "get_calendar_events":
                # Получить события из календаря
                async with self.async_session() as session:
                    result = await session.execute(
                        text("SELECT id, title, start_time, end_time, description FROM calendar_events WHERE user_id = :user_id ORDER BY start_time"),
                        {"user_id": user_id}
                    )
                    events = result.fetchall()
                    return {"success": True, "data": [{"id": e[0], "title": e[1], "start_time": str(e[2]), "end_time": str(e[3]) if e[3] else None, "description": e[4]} for e in events]}
            
            else:
                return {"success": False, "error": f"Unknown function: {function_name}"}
        
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return {"success": False, "error": str(e)}
