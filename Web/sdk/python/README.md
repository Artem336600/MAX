# Eidos SDK для Python

Python SDK для создания модулей для платформы Eidos.

## Установка

```bash
pip install eidos-sdk
```

Или для разработки:

```bash
cd sdk/python
pip install -e .
```

## Быстрый старт

### 1. Создание модуля

```python
from eidos_sdk import EidosModule, DataSchema, DataType

class SleepTracker(EidosModule):
    def __init__(self, api_key: str):
        super().__init__(
            name="Sleep Tracker",
            version="1.0.0",
            description="Отслеживание качества сна",
            api_key=api_key
        )
        
        # Определяем схему данных
        sleep_schema = DataSchema("sleep_records", {
            "quality": DataType.NUMBER,
            "duration": DataType.NUMBER,
            "date": DataType.DATE,
            "notes": DataType.STRING
        })
        
        self.add_schema(sleep_schema)
    
    async def on_message(self, message: str, user_id: str) -> str:
        """Обработка сообщений от пользователя"""
        if "сон" in message.lower():
            # Получаем последнюю запись
            last_sleep = await self.get_user_data(user_id, "last_sleep")
            
            if last_sleep:
                return f"Последний сон: {last_sleep['quality']}/10, {last_sleep['duration']} часов"
            else:
                return "Записей о сне пока нет"
        
        return "Не понял запрос"
    
    async def record_sleep(self, user_id: str, quality: int, duration: float, notes: str = ""):
        """Записать данные о сне"""
        sleep_data = {
            "quality": quality,
            "duration": duration,
            "notes": notes
        }
        
        await self.set_user_data(user_id, "last_sleep", sleep_data)
        
        # Отправляем уведомление
        await self.notify(
            user_id,
            "Сон записан",
            f"Качество: {quality}/10, Длительность: {duration}ч"
        )
```

### 2. Использование модуля

```python
import asyncio

async def main():
    # Ваш API ключ из Eidos
    api_key = "eidos_module_..."
    
    # Создаём модуль
    tracker = SleepTracker(api_key)
    
    # Записываем сон
    await tracker.record_sleep(
        user_id="user_123",
        quality=8,
        duration=7.5,
        notes="Хорошо выспался"
    )
    
    # Обрабатываем сообщение
    response = await tracker.on_message("Как я спал?", "user_123")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Основные возможности

### Работа с данными пользователя

```python
# Сохранить данные
await module.set_user_data(user_id, "key", {"value": 123})

# Получить данные
data = await module.get_user_data(user_id, "key")

# Удалить данные
await module.delete_user_data(user_id, "key")
```

### Уведомления

```python
await module.notify(
    user_id,
    title="Заголовок",
    message="Текст уведомления",
    priority="high"  # low, normal, high, critical
)
```

### Работа с календарём

```python
# Создать событие
await module.create_calendar_event(
    user_id,
    title="Встреча",
    start_time="2025-11-15T10:00:00",
    end_time="2025-11-15T11:00:00",
    description="Важная встреча"
)

# Получить события
events = await module.get_calendar_events(
    user_id,
    start_date="2025-11-15",
    end_date="2025-11-16"
)
```

### Вызов других модулей

```python
# Вызвать публичный API другого модуля
result = await module.call_module(
    module_id="fitness-tracker",
    endpoint="/public/today",
    user_id=user_id
)
```

## Хуки жизненного цикла

```python
class MyModule(EidosModule):
    async def on_install(self, user_id: str):
        """Вызывается при установке модуля"""
        print(f"Модуль установлен для {user_id}")
    
    async def on_uninstall(self, user_id: str):
        """Вызывается при удалении модуля"""
        print(f"Модуль удалён для {user_id}")
    
    async def on_enable(self, user_id: str):
        """Вызывается при включении модуля"""
        pass
    
    async def on_disable(self, user_id: str):
        """Вызывается при отключении модуля"""
        pass
```

## Схемы данных

```python
from eidos_sdk import DataSchema, DataType

# Определяем схему
schema = DataSchema("my_data", {
    "name": DataType.STRING,
    "age": DataType.NUMBER,
    "active": DataType.BOOLEAN,
    "created_at": DataType.DATETIME,
    "metadata": DataType.JSON
})

# Добавляем в модуль
module.add_schema(schema)
```

## Примеры

Смотрите папку `examples/` для полных примеров модулей:

- `sleep_tracker.py` - Отслеживание сна
- `habit_tracker.py` - Трекер привычек
- `finance_manager.py` - Управление финансами

## Документация

Полная документация доступна на https://docs.eidos.dev

## Лицензия

MIT
