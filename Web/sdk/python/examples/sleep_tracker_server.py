"""
Sleep Tracker как внешний сервис
Запускается локально и принимает запросы от Eidos
"""

import asyncio
import sys
sys.path.append('..')

from eidos_sdk import EidosModule, DataSchema, DataType
from eidos_sdk.server import ModuleServer

class SleepTrackerService(EidosModule):
    def __init__(self, api_key: str):
        super().__init__(
            name="Sleep Tracker Service",
            version="1.0.0",
            description="Внешний сервис для отслеживания сна",
            api_key=api_key,
            base_url="http://localhost:8001/api/v1"
        )
        
        # Схема данных
        sleep_schema = DataSchema("sleep_records", {
            "quality": DataType.NUMBER,
            "duration": DataType.NUMBER,
            "sleep_time": DataType.DATETIME,
            "wake_time": DataType.DATETIME,
            "notes": DataType.STRING,
            "mood": DataType.STRING
        })
        
        self.add_schema(sleep_schema)
    
    async def on_install(self, user_id: str):
        """При установке модуля"""
        print(f"✅ Module installed for user {user_id}")
        await self.notify(
            user_id,
            "Sleep Tracker установлен! 😴",
            "Начните отслеживать свой сон для лучшего здоровья"
        )
    
    async def on_message(self, message: str, user_id: str) -> str:
        """Обработка сообщений"""
        message_lower = message.lower()
        
        print(f"📨 Message from {user_id}: {message}")
        
        if "сон" in message_lower or "спал" in message_lower:
            return await self.get_sleep_stats(user_id)
        elif "записать" in message_lower:
            return "Используйте функцию record_sleep для записи сна"
        else:
            return "Спросите меня о вашем сне или запишите новую запись"
    
    async def record_sleep(self, user_id: str, data: dict) -> dict:
        """Записать данные о сне"""
        
        quality = data.get('quality', 5)
        duration = data.get('duration', 7)
        notes = data.get('notes', '')
        
        print(f"💤 Recording sleep for {user_id}: quality={quality}, duration={duration}")
        
        if not (0 <= quality <= 10):
            return {"error": "Quality must be between 0 and 10"}
        
        sleep_data = {
            "quality": quality,
            "duration": duration,
            "notes": notes
        }
        
        # Сохраняем
        await self.set_user_data(user_id, "last_sleep", sleep_data)
        
        # История
        history = await self.get_user_data(user_id, "sleep_history") or []
        history.append(sleep_data)
        
        if len(history) > 30:
            history = history[-30:]
        
        await self.set_user_data(user_id, "sleep_history", history)
        
        # Уведомление
        emoji = "😴" if quality >= 8 else "😐" if quality >= 5 else "😞"
        await self.notify(
            user_id,
            f"Сон записан {emoji}",
            f"Качество: {quality}/10, Длительность: {duration}ч"
        )
        
        return {
            "success": True,
            "message": "Sleep recorded",
            "data": sleep_data
        }
    
    async def get_sleep_stats(self, user_id: str) -> str:
        """Получить статистику"""
        
        last_sleep = await self.get_user_data(user_id, "last_sleep")
        history = await self.get_user_data(user_id, "sleep_history") or []
        
        if not last_sleep:
            return "У вас пока нет записей о сне"
        
        response = f"📊 Статистика сна\n\n"
        response += f"Последний сон:\n"
        response += f"  Качество: {last_sleep['quality']}/10\n"
        response += f"  Длительность: {last_sleep['duration']}ч\n"
        
        if history:
            avg_quality = sum(s['quality'] for s in history) / len(history)
            avg_duration = sum(s['duration'] for s in history) / len(history)
            
            response += f"\nЗа последние {len(history)} дней:\n"
            response += f"  Средняя качество: {avg_quality:.1f}/10\n"
            response += f"  Средняя длительность: {avg_duration:.1f}ч\n"
        
        return response

def main():
    print("=" * 60)
    print("Sleep Tracker Service")
    print("=" * 60)
    
    # API ключ модуля (получите из Eidos)
    API_KEY = input("\n🔑 Введите API ключ модуля: ").strip()
    
    if not API_KEY:
        print("❌ API ключ не указан!")
        return
    
    # Порт для сервера
    PORT = input("📡 Порт (по умолчанию 8080): ").strip() or "8080"
    PORT = int(PORT)
    
    # Создать модуль
    module = SleepTrackerService(API_KEY)
    
    # Создать сервер
    server = ModuleServer(module, host="0.0.0.0", port=PORT)
    
    # Добавить пользовательские endpoints
    async def record_sleep_endpoint(user_id: str, data: dict):
        return await module.record_sleep(user_id, data)
    
    async def stats_endpoint(user_id: str, data: dict):
        stats = await module.get_sleep_stats(user_id)
        return {"stats": stats}
    
    server.add_endpoint("record", record_sleep_endpoint)
    server.add_endpoint("stats", stats_endpoint)
    
    # Запустить
    print(f"\n💡 Добавьте в манифест модуля:")
    print(f'   "webhook_url": "http://localhost:{PORT}"')
    print()
    
    server.run()

if __name__ == "__main__":
    main()
