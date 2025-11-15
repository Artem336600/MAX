"""
Управление инструментами (tools) для AI
"""

from typing import List, Dict, Any


class Tool:
    """Описание инструмента для AI"""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        required: List[str] = None
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.required = required or []
    
    def to_dict(self) -> Dict:
        """Конвертировать в формат для AI API"""
        # Определить обязательные параметры
        required_params = self.required if self.required else [
            key for key, value in self.parameters.items()
            if not value.get('description', '').lower().endswith('(опционально)')
            and not value.get('description', '').lower().endswith('(optional)')
        ]
        
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": required_params
            }
        }


class ToolsManager:
    """Менеджер инструментов"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool):
        """Зарегистрировать инструмент"""
        self.tools[tool.name] = tool
    
    def add_tools(self, tools: List[Tool]):
        """Добавить несколько инструментов"""
        for tool in tools:
            self.register(tool)
    
    def count(self) -> int:
        """Получить количество инструментов"""
        return len(self.tools)
    
    def get_all(self) -> List[Dict]:
        """Получить все инструменты в формате для AI"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def get_tool(self, name: str) -> Tool:
        """Получить инструмент по имени"""
        return self.tools.get(name)


# Предопределенные инструменты для модулей

def create_sleep_tracker_tools() -> List[Tool]:
    """Создать инструменты для Sleep Tracker"""
    return [
        Tool(
            name="get_sleep_stats",
            description="Получить статистику сна пользователя",
            parameters={}
        ),
        Tool(
            name="create_sleep_record",
            description="Создать запись о сне. Вызывай ВСЕГДА когда пользователь упоминает сон.",
            parameters={
                "quality": {
                    "type": "integer",
                    "description": "Качество сна от 1 до 10"
                },
                "duration": {
                    "type": "number",
                    "description": "Длительность сна в часах"
                },
                "sleep_time": {
                    "type": "string",
                    "description": "Время засыпания ISO 8601 (опционально)"
                },
                "wake_time": {
                    "type": "string",
                    "description": "Время пробуждения ISO 8601 (опционально)"
                },
                "mood": {
                    "type": "string",
                    "description": "Настроение: great, good, normal, bad, terrible (опционально)"
                },
                "notes": {
                    "type": "string",
                    "description": "Заметки (опционально)"
                }
            },
            required=["quality", "duration"]
        )
    ]


def create_habit_tracker_tools() -> List[Tool]:
    """Создать инструменты для Habit Tracker"""
    return [
        Tool(
            name="get_habits",
            description="Получить список привычек пользователя",
            parameters={}
        ),
        Tool(
            name="create_habit",
            description="Создать новую привычку",
            parameters={
                "name": {
                    "type": "string",
                    "description": "Название привычки"
                },
                "frequency": {
                    "type": "string",
                    "description": "Частота: daily, weekly, monthly"
                },
                "description": {
                    "type": "string",
                    "description": "Описание (опционально)"
                },
                "icon": {
                    "type": "string",
                    "description": "Emoji иконка (опционально)"
                }
            },
            required=["name", "frequency"]
        ),
        Tool(
            name="log_habit",
            description="Отметить выполнение привычки",
            parameters={
                "habit_id": {
                    "type": "string",
                    "description": "ID привычки"
                },
                "notes": {
                    "type": "string",
                    "description": "Заметки (опционально)"
                }
            },
            required=["habit_id"]
        )
    ]


def create_finance_tools() -> List[Tool]:
    """Создать инструменты для Finance Manager"""
    return [
        Tool(
            name="get_finance_stats",
            description="Получить финансовую статистику",
            parameters={}
        ),
        Tool(
            name="create_transaction",
            description="Создать транзакцию (доход или расход)",
            parameters={
                "type": {
                    "type": "string",
                    "description": "Тип: income (доход) или expense (расход)"
                },
                "amount": {
                    "type": "number",
                    "description": "Сумма"
                },
                "category": {
                    "type": "string",
                    "description": "Категория: Продукты, Транспорт, Зарплата и т.д."
                },
                "description": {
                    "type": "string",
                    "description": "Описание (опционально)"
                },
                "date": {
                    "type": "string",
                    "description": "Дата ISO 8601 (опционально)"
                }
            },
            required=["type", "amount", "category"]
        )
    ]


def create_calendar_tools() -> List[Tool]:
    """Создать инструменты для Calendar"""
    return [
        Tool(
            name="create_calendar_event",
            description="Создать событие в календаре (встреча, напоминание)",
            parameters={
                "title": {
                    "type": "string",
                    "description": "Название события"
                },
                "start_time": {
                    "type": "string",
                    "description": "Время начала в формате ISO 8601 (например: 2024-11-19T19:00:00)"
                },
                "end_time": {
                    "type": "string",
                    "description": "Время окончания в формате ISO 8601 (опционально)"
                },
                "description": {
                    "type": "string",
                    "description": "Описание события (опционально)"
                },
                "reminder_minutes": {
                    "type": "integer",
                    "description": "За сколько минут до события отправить напоминание (опционально)"
                }
            },
            required=["title", "start_time"]
        ),
        Tool(
            name="get_calendar_events",
            description="Получить список событий из календаря",
            parameters={
                "start_date": {
                    "type": "string",
                    "description": "Начальная дата (опционально, по умолчанию сегодня)"
                },
                "end_date": {
                    "type": "string",
                    "description": "Конечная дата (опционально)"
                }
            },
            required=[]
        )
    ]


def create_all_tools() -> ToolsManager:
    """Создать все инструменты"""
    manager = ToolsManager()
    
    # Sleep Tracker
    for tool in create_sleep_tracker_tools():
        manager.register(tool)
    
    # Habit Tracker
    for tool in create_habit_tracker_tools():
        manager.register(tool)
    
    # Finance Manager
    for tool in create_finance_tools():
        manager.register(tool)
    
    # Calendar
    for tool in create_calendar_tools():
        manager.register(tool)
    
    return manager
