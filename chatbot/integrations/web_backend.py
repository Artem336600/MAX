"""
Интеграция MAKS бота с Web Backend
"""

import sys
import os

# Добавить путь к Web backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../Web/backend'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# Импорт моделей Web
from models.user import User
from models.sleep_tracker import SleepRecord
from models.habit_tracker import Habit, HabitLog
from models.finance_manager import Transaction

logger = logging.getLogger(__name__)


class WebBackendIntegration:
    """Интеграция MAKS бота с Web Backend"""
    
    def __init__(self, db_url: str = "sqlite+aiosqlite:///../../Web/backend/eidos.db"):
        """
        Инициализация
        
        Args:
            db_url: URL базы данных Web
        """
        # Преобразовать относительный путь в абсолютный
        if db_url.startswith("sqlite"):
            db_path = db_url.split("///")[1]
            abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), db_path))
            db_url = f"sqlite+aiosqlite:///{abs_path}"
        
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info(f"Connected to Web DB: {db_url}")
    
    async def get_or_create_user(self, maks_id: int, name: str) -> User:
        """
        Получить или создать пользователя по MAKS ID
        
        Args:
            maks_id: ID пользователя в MAKS
            name: Имя пользователя
        
        Returns:
            User объект
        """
        async with self.async_session() as session:
            # Попробовать найти по email (используем maks_id как email)
            email = f"maks_{maks_id}@bot.local"
            
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # Создать нового пользователя
                user = User(
                    email=email,
                    name=name,
                    password_hash="bot_user",  # Для ботов не нужен пароль
                    role="user"
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"Created new user for MAKS ID {maks_id}")
            
            return user
    
    async def create_sleep_record(
        self,
        user_id: str,
        quality: int,
        duration: float,
        sleep_time: Optional[str] = None,
        wake_time: Optional[str] = None,
        mood: Optional[str] = None,
        notes: Optional[str] = None
    ) -> SleepRecord:
        """Создать запись о сне"""
        async with self.async_session() as session:
            # Вычислить время если не указано
            now = datetime.utcnow()
            wake_dt = datetime.fromisoformat(wake_time.replace('Z', '+00:00')) if wake_time else now
            sleep_dt = datetime.fromisoformat(sleep_time.replace('Z', '+00:00')) if sleep_time else (wake_dt - timedelta(hours=duration))
            
            record = SleepRecord(
                user_id=user_id,
                quality=quality,
                duration=duration,
                sleep_time=sleep_dt,
                wake_time=wake_dt,
                mood=mood,
                notes=notes
            )
            
            session.add(record)
            await session.commit()
            await session.refresh(record)
            
            logger.info(f"Created sleep record for user {user_id}")
            return record
    
    async def get_sleep_stats(self, user_id: str) -> Dict[str, Any]:
        """Получить статистику сна"""
        async with self.async_session() as session:
            result = await session.execute(
                select(SleepRecord).where(SleepRecord.user_id == user_id)
            )
            records = result.scalars().all()
            
            if not records:
                return {
                    "total_records": 0,
                    "avg_quality": 0,
                    "avg_duration": 0
                }
            
            return {
                "total_records": len(records),
                "avg_quality": round(sum(r.quality for r in records) / len(records), 1),
                "avg_duration": round(sum(r.duration for r in records) / len(records), 1),
                "best_quality": max(r.quality for r in records),
                "worst_quality": min(r.quality for r in records)
            }
    
    async def create_habit(
        self,
        user_id: str,
        name: str,
        frequency: str,
        description: Optional[str] = None,
        icon: Optional[str] = None
    ) -> Habit:
        """Создать привычку"""
        async with self.async_session() as session:
            habit = Habit(
                user_id=user_id,
                name=name,
                description=description or "",
                frequency=frequency,
                icon=icon or "⭐",
                color="#6366F1",
                active=True
            )
            
            session.add(habit)
            await session.commit()
            await session.refresh(habit)
            
            logger.info(f"Created habit '{name}' for user {user_id}")
            return habit
    
    async def get_habits(self, user_id: str):
        """Получить список привычек"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Habit).where(
                    Habit.user_id == user_id,
                    Habit.active == True
                )
            )
            return result.scalars().all()
    
    async def log_habit(self, habit_id: str, notes: Optional[str] = None) -> HabitLog:
        """Отметить выполнение привычки"""
        async with self.async_session() as session:
            log = HabitLog(
                habit_id=habit_id,
                completed_at=datetime.utcnow(),
                notes=notes
            )
            
            session.add(log)
            await session.commit()
            await session.refresh(log)
            
            logger.info(f"Logged habit {habit_id}")
            return log
    
    async def create_transaction(
        self,
        user_id: str,
        type: str,
        amount: float,
        category: str,
        description: Optional[str] = None,
        date: Optional[str] = None
    ) -> Transaction:
        """Создать транзакцию"""
        async with self.async_session() as session:
            transaction = Transaction(
                user_id=user_id,
                type=type,
                amount=amount,
                category=category,
                description=description or "",
                date=datetime.fromisoformat(date.replace('Z', '+00:00')) if date else datetime.utcnow()
            )
            
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            
            logger.info(f"Created {type} transaction for user {user_id}: {amount}")
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
        """
        Выполнить функцию модуля
        
        Args:
            function_name: Имя функции
            arguments: Аргументы функции
            user_id: ID пользователя
        
        Returns:
            Результат выполнения
        """
        try:
            # Sleep Tracker
            if function_name == "create_sleep_record":
                record = await self.create_sleep_record(user_id=user_id, **arguments)
                return {
                    "success": True,
                    "data": {
                        "id": record.id,
                        "quality": record.quality,
                        "duration": record.duration
                    }
                }
            
            elif function_name == "get_sleep_stats":
                stats = await self.get_sleep_stats(user_id)
                return {"success": True, "data": stats}
            
            # Habit Tracker
            elif function_name == "create_habit":
                habit = await self.create_habit(user_id=user_id, **arguments)
                return {
                    "success": True,
                    "data": {
                        "id": habit.id,
                        "name": habit.name,
                        "frequency": habit.frequency
                    }
                }
            
            elif function_name == "get_habits":
                habits = await self.get_habits(user_id)
                return {
                    "success": True,
                    "data": [
                        {"id": h.id, "name": h.name, "frequency": h.frequency}
                        for h in habits
                    ]
                }
            
            elif function_name == "log_habit":
                log = await self.log_habit(**arguments)
                return {"success": True, "data": {"id": log.id}}
            
            # Finance Manager
            elif function_name == "create_transaction":
                transaction = await self.create_transaction(user_id=user_id, **arguments)
                return {
                    "success": True,
                    "data": {
                        "id": transaction.id,
                        "type": transaction.type,
                        "amount": transaction.amount
                    }
                }
            
            elif function_name == "get_finance_stats":
                stats = await self.get_finance_stats(user_id)
                return {"success": True, "data": stats}
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
        
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
