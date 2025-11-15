"""
Тестовый скрипт для проверки модуля Sleep Tracker
"""

import asyncio
import sys
sys.path.append('sdk/python')

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
            "quality": DataType.NUMBER,
            "duration": DataType.NUMBER,
            "sleep_time": DataType.DATETIME,
            "wake_time": DataType.DATETIME,
            "notes": DataType.STRING,
            "mood": DataType.STRING
        })
        
        self.add_schema(sleep_schema)
    
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
        
        return response

async def main():
    print("=== Тест модуля Sleep Tracker ===\n")
    
    # Замените на ваш API ключ из "Мои модули"
    API_KEY = input("Введите API ключ модуля: ").strip()
    
    if not API_KEY:
        print("❌ API ключ не указан!")
        return
    
    print(f"\n✅ Создание модуля...")
    tracker = SleepTracker(API_KEY)
    
    print(f"📦 Модуль: {tracker.name} v{tracker.version}")
    print(f"📝 Описание: {tracker.description}")
    print(f"🔑 API Key: {tracker.api_key[:20]}...")
    
    # Генерируем манифест
    manifest = tracker.to_manifest()
    print(f"\n📋 Манифест:")
    print(f"  - Название: {manifest['name']}")
    print(f"  - Версия: {manifest['version']}")
    print(f"  - Схем данных: {len(manifest['schemas'])}")
    
    print("\n✅ Модуль создан успешно!")
    print("\nТеперь вы можете:")
    print("1. Установить модуль через маркетплейс")
    print("2. Использовать его в чате с ИИ")
    print("3. ИИ будет видеть этот модуль и его функции")

if __name__ == "__main__":
    asyncio.run(main())
