"""
RAG (Retrieval-Augmented Generation) система для глубокой персонализации ИИ

Собирает и анализирует всю информацию о пользователе из модулей,
создает векторное представление для контекстного поиска.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import json

from models.module import Module, UserModule
from models.user import User
from models.chat import Message, Conversation
from models.calendar import CalendarEvent
from models.sleep_tracker import SleepRecord
from models.habit_tracker import Habit, HabitLog
from models.finance_manager import Transaction


class UserContext:
    """Контекст пользователя - вся собранная информация"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.profile: Dict[str, Any] = {}
        self.patterns: Dict[str, Any] = {}
        self.preferences: Dict[str, Any] = {}
        self.insights: List[Dict[str, Any]] = []
        self.last_updated: datetime = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "profile": self.profile,
            "patterns": self.patterns,
            "preferences": self.preferences,
            "insights": self.insights,
            "last_updated": self.last_updated.isoformat()
        }


class DataCollector:
    """Сборщик данных из всех источников"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def collect_user_data(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Собрать все данные пользователя за период"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        data = {
            "profile": await self._collect_profile(user_id),
            "sleep": await self._collect_sleep_data(user_id, start_date),
            "habits": await self._collect_habits_data(user_id, start_date),
            "finance": await self._collect_finance_data(user_id, start_date),
            "calendar": await self._collect_calendar_data(user_id, start_date),
            "conversations": await self._collect_conversation_data(user_id, start_date),
            "modules": await self._collect_module_data(user_id)
        }
        
        return data
    
    async def _collect_profile(self, user_id: str) -> Dict[str, Any]:
        """Базовая информация о пользователе"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {}
        
        return {
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat()
        }
    
    async def _collect_sleep_data(self, user_id: str, start_date: datetime) -> Dict[str, Any]:
        """Данные о сне"""
        result = await self.db.execute(
            select(SleepRecord)
            .where(
                and_(
                    SleepRecord.user_id == user_id,
                    SleepRecord.sleep_time >= start_date
                )
            )
            .order_by(desc(SleepRecord.sleep_time))
        )
        records = result.scalars().all()
        
        if not records:
            return {"available": False}
        
        total_duration = sum(r.duration for r in records if r.duration)
        avg_duration = total_duration / len(records) if records else 0
        avg_quality = sum(r.quality for r in records if r.quality) / len(records) if records else 0
        
        return {
            "available": True,
            "records_count": len(records),
            "avg_duration": avg_duration,
            "avg_quality": avg_quality,
            "recent_records": [
                {
                    "date": r.sleep_time.date().isoformat(),
                    "duration": r.duration,
                    "quality": r.quality
                }
                for r in records[:7]  # Последние 7 дней
            ]
        }
    
    async def _collect_habits_data(self, user_id: str, start_date: datetime) -> Dict[str, Any]:
        """Данные о привычках"""
        # Получить привычки
        habits_result = await self.db.execute(
            select(Habit).where(Habit.user_id == user_id)
        )
        habits = habits_result.scalars().all()
        
        if not habits:
            return {"available": False}
        
        # Получить логи
        logs_result = await self.db.execute(
            select(HabitLog)
            .join(Habit)
            .where(
                and_(
                    Habit.user_id == user_id,
                    HabitLog.completed_at >= start_date
                )
            )
        )
        logs = logs_result.scalars().all()
        
        # Анализ выполнения
        habit_stats = {}
        for habit in habits:
            habit_logs = [l for l in logs if l.habit_id == habit.id]
            completed = len(habit_logs)  # Все логи считаются выполненными
            # Рассчитать ожидаемое количество на основе частоты
            days_in_period = (datetime.utcnow() - start_date).days
            if habit.frequency == 'daily':
                expected = days_in_period
            elif habit.frequency == 'weekly':
                expected = days_in_period // 7
            else:  # monthly
                expected = days_in_period // 30
            
            habit_stats[habit.name] = {
                "completion_rate": completed / expected if expected > 0 else 0,
                "total_logs": completed,
                "completed": completed
            }
        
        return {
            "available": True,
            "habits_count": len(habits),
            "total_logs": len(logs),
            "habit_stats": habit_stats
        }
    
    async def _collect_finance_data(self, user_id: str, start_date: datetime) -> Dict[str, Any]:
        """Финансовые данные"""
        result = await self.db.execute(
            select(Transaction)
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_date
                )
            )
        )
        transactions = result.scalars().all()
        
        if not transactions:
            return {"available": False}
        
        income = sum(t.amount for t in transactions if t.amount > 0)
        expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        
        # Категории расходов
        categories = {}
        for t in transactions:
            if t.amount < 0:
                cat = t.category or "Другое"
                categories[cat] = categories.get(cat, 0) + abs(t.amount)
        
        return {
            "available": True,
            "transactions_count": len(transactions),
            "total_income": income,
            "total_expenses": expenses,
            "balance": income - expenses,
            "top_categories": sorted(
                categories.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    async def _collect_calendar_data(self, user_id: str, start_date: datetime) -> Dict[str, Any]:
        """Данные календаря"""
        result = await self.db.execute(
            select(CalendarEvent)
            .where(
                and_(
                    CalendarEvent.user_id == user_id,
                    CalendarEvent.start_time >= start_date
                )
            )
            .order_by(CalendarEvent.start_time)
        )
        events = result.scalars().all()
        
        if not events:
            return {"available": False}
        
        # Анализ типов событий
        event_types = {}
        for event in events:
            # Простая категоризация по ключевым словам
            title_lower = event.title.lower()
            if any(word in title_lower for word in ['встреча', 'meeting', 'созвон']):
                event_type = 'meetings'
            elif any(word in title_lower for word in ['работа', 'work', 'задача']):
                event_type = 'work'
            elif any(word in title_lower for word in ['спорт', 'тренировка', 'gym']):
                event_type = 'fitness'
            else:
                event_type = 'other'
            
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "available": True,
            "events_count": len(events),
            "event_types": event_types,
            "upcoming_events": [
                {
                    "title": e.title,
                    "start_time": e.start_time.isoformat(),
                    "description": e.description
                }
                for e in events[:10]  # Ближайшие 10
            ]
        }
    
    async def _collect_conversation_data(self, user_id: str, start_date: datetime) -> Dict[str, Any]:
        """Данные из разговоров с ИИ"""
        # Получить диалоги
        conversations_result = await self.db.execute(
            select(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.created_at >= start_date
                )
            )
        )
        conversations = conversations_result.scalars().all()
        
        if not conversations:
            return {"available": False}
        
        # Получить сообщения
        messages_result = await self.db.execute(
            select(Message)
            .join(Conversation)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Message.created_at >= start_date
                )
            )
        )
        messages = messages_result.scalars().all()
        
        # Анализ тем (простой подсчет ключевых слов)
        topics = {}
        for msg in messages:
            if msg.role == "user":
                # Извлечь ключевые слова (упрощенно)
                words = msg.content.lower().split()
                for word in words:
                    if len(word) > 4:  # Только длинные слова
                        topics[word] = topics.get(word, 0) + 1
        
        # Топ-10 тем
        top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "available": True,
            "conversations_count": len(conversations),
            "messages_count": len(messages),
            "top_topics": [{"word": word, "count": count} for word, count in top_topics]
        }
    
    async def _collect_module_data(self, user_id: str) -> Dict[str, Any]:
        """Данные об установленных модулях"""
        result = await self.db.execute(
            select(Module, UserModule.enabled)
            .join(UserModule)
            .where(UserModule.user_id == user_id)
        )
        
        modules_data = []
        for module, enabled in result.all():
            modules_data.append({
                "id": module.id,
                "name": module.name,
                "description": module.description,
                "enabled": enabled,
                "status": module.status
            })
        
        return {
            "installed_count": len(modules_data),
            "enabled_count": len([m for m in modules_data if m["enabled"]]),
            "modules": modules_data
        }


class PatternAnalyzer:
    """Анализатор паттернов поведения"""
    
    def analyze_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Выявить паттерны в данных пользователя"""
        
        patterns = {
            "sleep_pattern": self._analyze_sleep_pattern(data.get("sleep", {})),
            "productivity_pattern": self._analyze_productivity(data),
            "financial_pattern": self._analyze_financial_behavior(data.get("finance", {})),
            "habit_consistency": self._analyze_habit_consistency(data.get("habits", {})),
            "time_management": self._analyze_time_management(data.get("calendar", {}))
        }
        
        return patterns
    
    def _analyze_sleep_pattern(self, sleep_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ паттерна сна"""
        if not sleep_data.get("available"):
            return {"status": "no_data"}
        
        avg_duration = sleep_data.get("avg_duration", 0)
        avg_quality = sleep_data.get("avg_quality", 0)
        
        # Оценка качества сна
        if avg_duration >= 7 and avg_quality >= 4:
            status = "excellent"
            recommendation = "Отличный режим сна! Продолжай в том же духе."
        elif avg_duration >= 6 and avg_quality >= 3:
            status = "good"
            recommendation = "Хороший сон, но можно улучшить качество."
        else:
            status = "needs_improvement"
            recommendation = "Стоит уделить внимание качеству и продолжительности сна."
        
        return {
            "status": status,
            "avg_duration": avg_duration,
            "avg_quality": avg_quality,
            "recommendation": recommendation
        }
    
    def _analyze_productivity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ продуктивности"""
        habits = data.get("habits", {})
        calendar = data.get("calendar", {})
        
        if not habits.get("available") and not calendar.get("available"):
            return {"status": "no_data"}
        
        # Оценка на основе выполнения привычек и событий
        habit_completion = 0
        if habits.get("available"):
            stats = habits.get("habit_stats", {})
            if stats:
                habit_completion = sum(s["completion_rate"] for s in stats.values()) / len(stats)
        
        return {
            "habit_completion_rate": habit_completion,
            "status": "high" if habit_completion > 0.7 else "medium" if habit_completion > 0.4 else "low",
            "recommendation": self._get_productivity_recommendation(habit_completion)
        }
    
    def _get_productivity_recommendation(self, rate: float) -> str:
        if rate > 0.7:
            return "Отличная продуктивность! Ты справляешься с большинством задач."
        elif rate > 0.4:
            return "Неплохо, но есть куда расти. Попробуй планировать задачи заранее."
        else:
            return "Стоит пересмотреть подход к планированию. Начни с малого."
    
    def _analyze_financial_behavior(self, finance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ финансового поведения"""
        if not finance_data.get("available"):
            return {"status": "no_data"}
        
        balance = finance_data.get("balance", 0)
        income = finance_data.get("total_income", 0)
        expenses = finance_data.get("total_expenses", 0)
        
        savings_rate = (balance / income * 100) if income > 0 else 0
        
        return {
            "savings_rate": savings_rate,
            "status": "healthy" if savings_rate > 20 else "moderate" if savings_rate > 10 else "concerning",
            "top_expense_categories": finance_data.get("top_categories", []),
            "recommendation": self._get_financial_recommendation(savings_rate)
        }
    
    def _get_financial_recommendation(self, rate: float) -> str:
        if rate > 20:
            return "Отличное управление финансами! Продолжай откладывать."
        elif rate > 10:
            return "Неплохо, но можно увеличить сбережения."
        else:
            return "Стоит пересмотреть расходы и начать откладывать больше."
    
    def _analyze_habit_consistency(self, habits_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ постоянства привычек"""
        if not habits_data.get("available"):
            return {"status": "no_data"}
        
        stats = habits_data.get("habit_stats", {})
        if not stats:
            return {"status": "no_habits"}
        
        # Средняя консистентность
        avg_consistency = sum(s["completion_rate"] for s in stats.values()) / len(stats)
        
        return {
            "avg_consistency": avg_consistency,
            "status": "consistent" if avg_consistency > 0.7 else "inconsistent",
            "strongest_habits": [
                name for name, data in stats.items()
                if data["completion_rate"] > 0.8
            ],
            "needs_work": [
                name for name, data in stats.items()
                if data["completion_rate"] < 0.5
            ]
        }
    
    def _analyze_time_management(self, calendar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ управления временем"""
        if not calendar_data.get("available"):
            return {"status": "no_data"}
        
        event_types = calendar_data.get("event_types", {})
        total_events = sum(event_types.values())
        
        # Баланс между работой и личным временем
        work_events = event_types.get("work", 0) + event_types.get("meetings", 0)
        personal_events = event_types.get("fitness", 0) + event_types.get("other", 0)
        
        work_ratio = work_events / total_events if total_events > 0 else 0
        
        return {
            "total_events": total_events,
            "work_ratio": work_ratio,
            "balance": "good" if 0.4 <= work_ratio <= 0.7 else "needs_adjustment",
            "recommendation": self._get_time_management_recommendation(work_ratio)
        }
    
    def _get_time_management_recommendation(self, work_ratio: float) -> str:
        if work_ratio > 0.8:
            return "Слишком много рабочих событий. Добавь время для отдыха и хобби."
        elif work_ratio < 0.3:
            return "Мало рабочих событий. Возможно, стоит структурировать рабочее время."
        else:
            return "Хороший баланс между работой и личным временем!"


class RAGSystem:
    """Главная RAG-система"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.collector = DataCollector(db)
        self.analyzer = PatternAnalyzer()
        self._context_cache: Dict[str, UserContext] = {}
    
    async def build_user_context(self, user_id: str, force_refresh: bool = False) -> UserContext:
        """Построить полный контекст пользователя"""
        
        # Проверить кэш
        if not force_refresh and user_id in self._context_cache:
            cached = self._context_cache[user_id]
            # Если кэш свежий (< 1 часа), вернуть его
            if (datetime.utcnow() - cached.last_updated).seconds < 3600:
                return cached
        
        # Собрать данные
        data = await self.collector.collect_user_data(user_id)
        
        # Проанализировать паттерны
        patterns = self.analyzer.analyze_patterns(data)
        
        # Создать контекст
        context = UserContext(user_id)
        context.profile = data.get("profile", {})
        context.patterns = patterns
        
        # Извлечь предпочтения из данных
        context.preferences = self._extract_preferences(data)
        
        # Сгенерировать инсайты
        context.insights = self._generate_insights(data, patterns)
        
        # Кэшировать
        self._context_cache[user_id] = context
        
        return context
    
    def _extract_preferences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечь предпочтения пользователя"""
        preferences = {}
        
        # Из разговоров
        conversations = data.get("conversations", {})
        if conversations.get("available"):
            top_topics = conversations.get("top_topics", [])
            preferences["interests"] = [t["word"] for t in top_topics[:5]]
        
        # Из модулей
        modules = data.get("modules", {})
        enabled_modules = [
            m["name"] for m in modules.get("modules", [])
            if m.get("enabled")
        ]
        preferences["active_modules"] = enabled_modules
        
        return preferences
    
    def _generate_insights(
        self,
        data: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Сгенерировать инсайты о пользователе"""
        insights = []
        
        # Инсайт о сне
        sleep_pattern = patterns.get("sleep_pattern", {})
        if sleep_pattern.get("status") != "no_data":
            insights.append({
                "category": "sleep",
                "title": "Качество сна",
                "description": sleep_pattern.get("recommendation", ""),
                "priority": "high" if sleep_pattern.get("status") == "needs_improvement" else "low"
            })
        
        # Инсайт о продуктивности
        productivity = patterns.get("productivity_pattern", {})
        if productivity.get("status") != "no_data":
            insights.append({
                "category": "productivity",
                "title": "Продуктивность",
                "description": productivity.get("recommendation", ""),
                "priority": "high" if productivity.get("status") == "low" else "medium"
            })
        
        # Инсайт о финансах
        financial = patterns.get("financial_pattern", {})
        if financial.get("status") != "no_data":
            insights.append({
                "category": "finance",
                "title": "Финансовое здоровье",
                "description": financial.get("recommendation", ""),
                "priority": "high" if financial.get("status") == "concerning" else "low"
            })
        
        return insights
    
    async def get_context_for_ai(self, user_id: str) -> str:
        """Получить контекст для ИИ в текстовом формате"""
        context = await self.build_user_context(user_id)
        
        prompt = f"""
# Контекст пользователя

## Профиль
Имя: {context.profile.get('name', 'Пользователь')}

## Паттерны поведения
"""
        
        # Добавить паттерны
        for pattern_name, pattern_data in context.patterns.items():
            if pattern_data.get("status") != "no_data":
                prompt += f"\n### {pattern_name}\n"
                prompt += f"Статус: {pattern_data.get('status', 'unknown')}\n"
                if "recommendation" in pattern_data:
                    prompt += f"Рекомендация: {pattern_data['recommendation']}\n"
        
        # Добавить инсайты
        if context.insights:
            prompt += "\n## Важные инсайты\n"
            for insight in context.insights:
                prompt += f"- [{insight['priority']}] {insight['title']}: {insight['description']}\n"
        
        # Добавить предпочтения
        if context.preferences:
            prompt += "\n## Предпочтения\n"
            if "interests" in context.preferences:
                prompt += f"Интересы: {', '.join(context.preferences['interests'])}\n"
            if "active_modules" in context.preferences:
                prompt += f"Активные модули: {', '.join(context.preferences['active_modules'])}\n"
        
        return prompt


# Глобальный экземпляр
_rag_system: Optional[RAGSystem] = None

def get_rag_system(db: AsyncSession) -> RAGSystem:
    """Получить глобальный экземпляр RAG-системы"""
    return RAGSystem(db)
