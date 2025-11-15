"""
Пример модуля: Sleep Tracker
Отслеживание качества сна
"""

import asyncio
from eidos_sdk import EidosModule, DataSchema, DataType

class SleepTracker(EidosModule):
    def __init__(self, api_key: str):
        super().__init__(
            name="Sleep Tracker",
            version="1.0.0",
            description="Отслеживание качества сна и анализ паттернов",
            api_key=api_key
        )
        
        # Схема данных для записей о сне
        sleep_schema = DataSchema("sleep_records", {
            "quality": DataType.NUMBER,  # 0-10
            "duration": DataType.NUMBER,  # часы
            "sleep_time": DataType.DATETIME,
            "wake_time": DataType.DATETIME,
            "notes": DataType.STRING,
            "mood": DataType.STRING
        })
        
        self.add_schema(sleep_schema)
    
    async def on_install(self, user_id: str):
        """При установке модуля"""
        await self.notify(
            user_id,
            "Sleep Tracker установлен! 😴",
            "Начните отслеживать свой сон для лучшего здоровья"
        )
    
    async def on_message(self, message: str, user_id: str) -> str:
        """Обработка сообщений от пользователя"""
        message_lower = message.lower()
        
        if "сон" in message_lower or "спал" in message_lower:
            return await self.get_sleep_stats(user_id)
        elif "записать" in message_lower:
            return "Используйте метод record_sleep() для записи сна"
        else:
            return "Спросите меня о вашем сне или запишите новую запись"
    
    async def record_sleep(
        self,
        user_id: str,
        quality: int,
        duration: float,
        sleep_time: str,
        wake_time: str,
        notes: str = "",
        mood: str = "normal"
    ):
        """Записать данные о сне"""
        
        if not (0 <= quality <= 10):
            raise ValueError("Quality must be between 0 and 10")
        
        sleep_data = {
            "quality": quality,
            "duration": duration,
            "sleep_time": sleep_time,
            "wake_time": wake_time,
            "notes": notes,
            "mood": mood
        }
        
        # Сохраняем последнюю запись
        await self.set_user_data(user_id, "last_sleep", sleep_data)
        
        # Получаем историю
        history = await self.get_user_data(user_id, "sleep_history") or []
        history.append(sleep_data)
        
        # Храним только последние 30 записей
        if len(history) > 30:
            history = history[-30:]
        
        await self.set_user_data(user_id, "sleep_history", history)
        
        # Отправляем уведомление
        emoji = "😴" if quality >= 8 else "😐" if quality >= 5 else "😞"
        await self.notify(
            user_id,
            f"Сон записан {emoji}",
            f"Качество: {quality}/10, Длительность: {duration}ч",
            priority="normal"
        )
        
        # Создаём напоминание на следующий день
        await self.create_calendar_event(
            user_id,
            title="Записать сон",
            start_time=wake_time,
            description="Не забудьте записать качество сна"
        )
        
        return sleep_data
    
    async def get_sleep_stats(self, user_id: str) -> str:
        """Получить статистику сна"""
        
        last_sleep = await self.get_user_data(user_id, "last_sleep")
        history = await self.get_user_data(user_id, "sleep_history") or []
        
        if not last_sleep:
            return "У вас пока нет записей о сне. Запишите первую запись!"
        
        # Последний сон
        response = f"📊 Статистика сна\n\n"
        response += f"Последний сон:\n"
        response += f"  Качество: {last_sleep['quality']}/10\n"
        response += f"  Длительность: {last_sleep['duration']}ч\n"
        
        if history:
            # Средние значения
            avg_quality = sum(s['quality'] for s in history) / len(history)
            avg_duration = sum(s['duration'] for s in history) / len(history)
            
            response += f"\nЗа последние {len(history)} дней:\n"
            response += f"  Средняя качество: {avg_quality:.1f}/10\n"
            response += f"  Средняя длительность: {avg_duration:.1f}ч\n"
            
            # Тренд
            if len(history) >= 7:
                recent_quality = sum(s['quality'] for s in history[-7:]) / 7
                older_quality = sum(s['quality'] for s in history[-14:-7]) / 7 if len(history) >= 14 else recent_quality
                
                if recent_quality > older_quality + 0.5:
                    response += "\n📈 Качество сна улучшается!"
                elif recent_quality < older_quality - 0.5:
                    response += "\n📉 Качество сна ухудшается"
                else:
                    response += "\n➡️ Качество сна стабильное"
        
        return response
    
    async def analyze_patterns(self, user_id: str) -> dict:
        """Анализ паттернов сна"""
        
        history = await self.get_user_data(user_id, "sleep_history") or []
        
        if len(history) < 7:
            return {"error": "Недостаточно данных для анализа (минимум 7 дней)"}
        
        # Анализ
        avg_quality = sum(s['quality'] for s in history) / len(history)
        avg_duration = sum(s['duration'] for s in history) / len(history)
        
        # Рекомендации
        recommendations = []
        
        if avg_quality < 7:
            recommendations.append("Попробуйте ложиться спать раньше")
        
        if avg_duration < 7:
            recommendations.append("Увеличьте длительность сна до 7-8 часов")
        elif avg_duration > 9:
            recommendations.append("Возможно, вы спите слишком много")
        
        return {
            "avg_quality": avg_quality,
            "avg_duration": avg_duration,
            "total_records": len(history),
            "recommendations": recommendations
        }

# Пример использования
async def main():
    # Замените на ваш API ключ
    API_KEY = "eidos_module_..."
    
    tracker = SleepTracker(API_KEY)
    
    # Записываем сон
    await tracker.record_sleep(
        user_id="user_123",
        quality=8,
        duration=7.5,
        sleep_time="2025-11-14T23:00:00",
        wake_time="2025-11-15T06:30:00",
        notes="Хорошо выспался",
        mood="great"
    )
    
    # Получаем статистику
    stats = await tracker.get_sleep_stats("user_123")
    print(stats)
    
    # Анализ паттернов
    analysis = await tracker.analyze_patterns("user_123")
    print(analysis)

if __name__ == "__main__":
    asyncio.run(main())
