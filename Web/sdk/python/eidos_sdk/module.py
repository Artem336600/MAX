"""
Базовый класс для модулей Eidos
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from .client import EidosClient

class DataType(str, Enum):
    """Типы данных для схем"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"

class DataSchema:
    """Схема данных модуля"""
    
    def __init__(self, name: str, fields: Dict[str, DataType]):
        self.name = name
        self.fields = fields
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "fields": {k: v.value for k, v in self.fields.items()}
        }

class EidosModule:
    """Базовый класс для модулей Eidos"""
    
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        api_key: str,
        base_url: str = "http://localhost:8001/api/v1"
    ):
        self.name = name
        self.version = version
        self.description = description
        self.api_key = api_key
        self.base_url = base_url
        self.client = EidosClient(api_key, base_url)
        self.schemas: List[DataSchema] = []
    
    def add_schema(self, schema: DataSchema):
        """Добавить схему данных"""
        self.schemas.append(schema)
    
    # Хуки жизненного цикла
    async def on_install(self, user_id: str):
        """Вызывается при установке модуля"""
        pass
    
    async def on_uninstall(self, user_id: str):
        """Вызывается при удалении модуля"""
        pass
    
    async def on_enable(self, user_id: str):
        """Вызывается при включении модуля"""
        pass
    
    async def on_disable(self, user_id: str):
        """Вызывается при отключении модуля"""
        pass
    
    # Обработка сообщений
    async def on_message(self, message: str, user_id: str) -> str:
        """Обработка сообщения от пользователя"""
        return "Модуль получил сообщение"
    
    # Работа с данными пользователя
    async def get_user_data(self, user_id: str, key: str) -> Optional[Any]:
        """Получить данные пользователя"""
        return await self.client.get_user_data(user_id, key)
    
    async def set_user_data(self, user_id: str, key: str, value: Any):
        """Сохранить данные пользователя"""
        await self.client.set_user_data(user_id, key, value)
    
    async def delete_user_data(self, user_id: str, key: str):
        """Удалить данные пользователя"""
        await self.client.delete_user_data(user_id, key)
    
    # Уведомления
    async def notify(self, user_id: str, title: str, message: str, priority: str = "normal"):
        """Отправить уведомление пользователю"""
        await self.client.send_notification(user_id, title, message, priority)
    
    # Работа с календарём
    async def create_calendar_event(
        self,
        user_id: str,
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Создать событие в календаре"""
        return await self.client.create_calendar_event(
            user_id, title, start_time, end_time, description
        )
    
    async def get_calendar_events(self, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Получить события из календаря"""
        return await self.client.get_calendar_events(user_id, start_date, end_date)
    
    # Вызов других модулей
    async def call_module(self, module_id: str, endpoint: str, user_id: str, **kwargs):
        """Вызвать публичный API другого модуля"""
        return await self.client.call_module(module_id, endpoint, user_id, **kwargs)
    
    def to_manifest(self) -> Dict:
        """Сгенерировать манифест модуля"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "schemas": [schema.to_dict() for schema in self.schemas]
        }
