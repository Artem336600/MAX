"""
Клиент для взаимодействия с Eidos API
"""

import aiohttp
from typing import Dict, Any, Optional

class EidosClient:
    """Клиент для работы с Eidos API"""
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8001/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs):
        """Выполнить HTTP запрос"""
        url = f"{self.base_url}{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
    
    # Данные пользователя
    async def get_user_data(self, user_id: str, key: str) -> Optional[Any]:
        """Получить данные пользователя"""
        try:
            data = await self._request("GET", f"/users/{user_id}/data/{key}")
            return data.get("value")
        except:
            return None
    
    async def set_user_data(self, user_id: str, key: str, value: Any):
        """Сохранить данные пользователя"""
        await self._request("POST", f"/users/{user_id}/data", json={"key": key, "value": value})
    
    async def delete_user_data(self, user_id: str, key: str):
        """Удалить данные пользователя"""
        await self._request("DELETE", f"/users/{user_id}/data/{key}")
    
    # Уведомления
    async def send_notification(self, user_id: str, title: str, message: str, priority: str = "normal"):
        """Отправить уведомление"""
        await self._request("POST", "/notifications", json={
            "user_id": user_id,
            "title": title,
            "message": message,
            "priority": priority
        })
    
    # Календарь
    async def create_calendar_event(
        self,
        user_id: str,
        title: str,
        start_time: str,
        end_time: Optional[str] = None,
        description: Optional[str] = None
    ):
        """Создать событие в календаре"""
        return await self._request("POST", "/calendar/events", json={
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "description": description
        })
    
    async def get_calendar_events(self, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Получить события из календаря"""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return await self._request("GET", "/calendar/events", params=params)
    
    # Вызов других модулей
    async def call_module(self, module_id: str, endpoint: str, user_id: str, **kwargs):
        """Вызвать публичный API другого модуля"""
        return await self._request("POST", f"/modules/{module_id}/call", json={
            "endpoint": endpoint,
            "user_id": user_id,
            **kwargs
        })
