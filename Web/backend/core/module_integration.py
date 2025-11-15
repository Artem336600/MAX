"""
Интеграция модулей с ИИ
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.module import Module, UserModule

class ModuleFunction:
    """Описание функции модуля"""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        module_id: str,
        endpoint: str,
        required: List[str] = None
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.module_id = module_id
        self.endpoint = endpoint
        self.required = required or []
    
    def to_openai_function(self) -> Dict:
        """Конвертировать в формат OpenAI function"""
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

class AIContextBuilder:
    """Построение контекста для ИИ с учётом модулей"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_modules(self, user_id: str) -> List[Module]:
        """Получить активные модули пользователя"""
        result = await self.db.execute(
            select(Module)
            .join(UserModule)
            .where(
                UserModule.user_id == user_id,
                UserModule.enabled == True
            )
        )
        return result.scalars().all()
    
    async def build_system_prompt(self, user_id: str, user_name: str) -> str:
        """Построить system prompt с учётом модулей"""
        
        modules = await self.get_user_modules(user_id)
        
        prompt = f"""Ты персональный ИИ-ассистент пользователя {user_name}.

Ты помогаешь пользователю управлять его жизнью через модульную систему Eidos.

У пользователя установлены следующие модули:
"""
        
        # Встроенные модули
        prompt += "- Календарь (встроенный): управление событиями и напоминаниями\n"
        prompt += "- Sleep Tracker (встроенный): отслеживание качества сна\n"
        prompt += "- Habit Tracker (встроенный): трекер привычек и целей\n"
        prompt += "- Finance Manager (встроенный): управление финансами и бюджетом\n"
        
        # Установленные модули из маркетплейса
        if modules:
            for module in modules:
                manifest = module.manifest or {}
                description = manifest.get('description', module.description)
                prompt += f"- {module.name}: {description}\n"
        
        prompt += """
Доступные функции:

Календарь:
- create_calendar_event: создать событие в календаре
- get_calendar_events: получить список событий

Сон:
- get_sleep_stats: получить статистику сна
- create_sleep_record: создать запись о сне (качество, длительность, время)

Привычки:
- get_habits: получить список привычек пользователя
- get_habit_stats: получить статистику привычек
- create_habit: создать новую привычку
- log_habit: отметить выполнение привычки

Финансы:
- get_finance_stats: получить финансовую статистику (баланс, доходы, расходы)
- get_transactions: получить список транзакций
- create_transaction: создать транзакцию (доход или расход)
"""
        
        # Добавляем функции модулей
        for module in modules:
            manifest = module.manifest or {}
            functions = manifest.get('functions', [])
            for func in functions:
                prompt += f"- {func['name']}: {func['description']}\n"
        
        prompt += """
Отвечай на русском языке, будь дружелюбным и полезным.
Используй эмодзи для улучшения восприятия.
Если пользователь просит что-то сделать - используй соответствующую функцию.
Если нужной функции нет - объясни это пользователю.
"""
        
        return prompt
    
    async def get_available_functions(self, user_id: str) -> List[ModuleFunction]:
        """Получить список доступных функций для ИИ"""
        
        modules = await self.get_user_modules(user_id)
        functions = []
        
        # Встроенные функции календаря
        functions.append(ModuleFunction(
            name="create_calendar_event",
            description="Создать событие в календаре пользователя",
            parameters={
                "title": {
                    "type": "string",
                    "description": "Название события"
                },
                "start_time": {
                    "type": "string",
                    "description": "Время начала в формате ISO 8601"
                },
                "end_time": {
                    "type": "string",
                    "description": "Время окончания в формате ISO 8601 (опционально)"
                },
                "description": {
                    "type": "string",
                    "description": "Описание события (опционально)"
                }
            },
            module_id="calendar",
            endpoint="/calendar/events"
        ))
        
        functions.append(ModuleFunction(
            name="get_calendar_events",
            description="Получить события из календаря",
            parameters={
                "start_date": {
                    "type": "string",
                    "description": "Начальная дата в формате ISO 8601 (опционально)"
                },
                "end_date": {
                    "type": "string",
                    "description": "Конечная дата в формате ISO 8601 (опционально)"
                }
            },
            module_id="calendar",
            endpoint="/calendar/events"
        ))
        
        # Sleep Tracker функции
        functions.append(ModuleFunction(
            name="get_sleep_stats",
            description="Получить статистику сна пользователя",
            parameters={},
            module_id="sleep_tracker",
            endpoint="/sleep/stats"
        ))
        
        functions.append(ModuleFunction(
            name="create_sleep_record",
            description="Создать запись о сне пользователя. Вызывай ВСЕГДА когда пользователь упоминает сон. Если время не указано - вычисли примерное время на основе текущего времени и длительности сна.",
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
                    "description": "Время засыпания в формате ISO 8601. Если не указано - вычисли как (текущее время - длительность сна)"
                },
                "wake_time": {
                    "type": "string",
                    "description": "Время пробуждения в формате ISO 8601. Если не указано - используй текущее время"
                },
                "mood": {
                    "type": "string",
                    "description": "Настроение: great, good, normal, bad, terrible (опционально)"
                },
                "notes": {
                    "type": "string",
                    "description": "Заметки о сне (опционально)"
                }
            },
            module_id="sleep_tracker",
            endpoint="/sleep/records",
            required=["quality", "duration"]
        ))
        
        # Habit Tracker функции
        functions.append(ModuleFunction(
            name="get_habits",
            description="Получить список привычек пользователя",
            parameters={},
            module_id="habit_tracker",
            endpoint="/habits"
        ))
        
        functions.append(ModuleFunction(
            name="get_habit_stats",
            description="Получить статистику привычек пользователя",
            parameters={},
            module_id="habit_tracker",
            endpoint="/habits/stats/overview"
        ))
        
        functions.append(ModuleFunction(
            name="create_habit",
            description="Создать новую привычку для пользователя",
            parameters={
                "name": {
                    "type": "string",
                    "description": "Название привычки"
                },
                "description": {
                    "type": "string",
                    "description": "Описание привычки (опционально)"
                },
                "frequency": {
                    "type": "string",
                    "description": "Частота: daily, weekly, monthly"
                },
                "icon": {
                    "type": "string",
                    "description": "Emoji иконка (опционально)"
                }
            },
            module_id="habit_tracker",
            endpoint="/habits"
        ))
        
        functions.append(ModuleFunction(
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
            module_id="habit_tracker",
            endpoint="/habits/{habit_id}/log"
        ))
        
        # Finance Manager функции
        functions.append(ModuleFunction(
            name="get_finance_stats",
            description="Получить финансовую статистику пользователя (баланс, доходы, расходы)",
            parameters={},
            module_id="finance_manager",
            endpoint="/finance/stats"
        ))
        
        functions.append(ModuleFunction(
            name="get_transactions",
            description="Получить список транзакций пользователя",
            parameters={},
            module_id="finance_manager",
            endpoint="/finance/transactions"
        ))
        
        functions.append(ModuleFunction(
            name="create_transaction",
            description="Создать финансовую транзакцию (доход или расход)",
            parameters={
                "type": {
                    "type": "string",
                    "description": "Тип транзакции: income (доход) или expense (расход)"
                },
                "amount": {
                    "type": "number",
                    "description": "Сумма транзакции"
                },
                "category": {
                    "type": "string",
                    "description": "Категория: Продукты, Транспорт, Развлечения, Зарплата и т.д."
                },
                "description": {
                    "type": "string",
                    "description": "Описание транзакции (опционально)"
                },
                "date": {
                    "type": "string",
                    "description": "Дата транзакции в формате ISO 8601 (опционально, по умолчанию сегодня)"
                }
            },
            module_id="finance_manager",
            endpoint="/finance/transactions"
        ))
        
        # Функции модулей
        for module in modules:
            manifest = module.manifest or {}
            module_functions = manifest.get('functions', [])
            
            for func in module_functions:
                functions.append(ModuleFunction(
                    name=func['name'],
                    description=func['description'],
                    parameters=func.get('parameters', {}),
                    module_id=module.id,
                    endpoint=func.get('endpoint', '/execute')
                ))
        
        return functions
    
    async def execute_function(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Any:
        """Выполнить функцию модуля"""
        
        functions = await self.get_available_functions(user_id)
        
        # Найти функцию
        func = None
        for f in functions:
            if f.name == function_name:
                func = f
                break
        
        if not func:
            raise ValueError(f"Function {function_name} not found")
        
        # Выполнить функцию встроенного модуля
        if func.module_id in ['sleep_tracker', 'habit_tracker', 'finance_manager', 'calendar']:
            return await self._execute_builtin_function(func, arguments, user_id)
        
        # Для пользовательских модулей - вызов через HTTP
        # TODO: реализовать вызов пользовательских модулей
        return {
            "success": True,
            "message": f"Function {function_name} executed",
            "data": arguments
        }
    
    async def _execute_builtin_function(
        self,
        func: ModuleFunction,
        arguments: Dict[str, Any],
        user_id: str
    ) -> Any:
        """Выполнить функцию встроенного модуля"""
        import httpx
        from api.auth import create_access_token
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Создать токен для запроса
        token = create_access_token({"sub": user_id})
        
        # Определить метод HTTP
        method = "POST" if func.name.startswith("create_") or func.name.startswith("log_") else "GET"
        
        # Построить URL
        base_url = "http://localhost:8001"
        url = f"{base_url}/api/v1{func.endpoint}"
        
        logger.info(f"Executing builtin function: {func.name}")
        logger.info(f"Method: {method}, URL: {url}")
        logger.info(f"Arguments: {arguments}")
        
        # Выполнить запрос
        async with httpx.AsyncClient() as client:
            if method == "POST":
                response = await client.post(
                    url,
                    json=arguments,
                    headers={"Authorization": f"Bearer {token}"}
                )
            else:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"}
                )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text}")
            
            if response.status_code >= 400:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
            
            return {
                "success": True,
                "data": response.json()
            }

class ModuleRegistry:
    """Реестр модулей для быстрого доступа"""
    
    def __init__(self):
        self._modules: Dict[str, Module] = {}
        self._user_modules: Dict[str, List[str]] = {}
    
    async def load_modules(self, db: AsyncSession):
        """Загрузить модули из БД"""
        result = await db.execute(select(Module))
        modules = result.scalars().all()
        
        for module in modules:
            self._modules[module.id] = module
    
    async def load_user_modules(self, db: AsyncSession, user_id: str):
        """Загрузить модули пользователя"""
        result = await db.execute(
            select(UserModule.module_id)
            .where(
                UserModule.user_id == user_id,
                UserModule.enabled == True
            )
        )
        
        module_ids = [row[0] for row in result.all()]
        self._user_modules[user_id] = module_ids
    
    def get_module(self, module_id: str) -> Optional[Module]:
        """Получить модуль по ID"""
        return self._modules.get(module_id)
    
    def get_user_modules(self, user_id: str) -> List[Module]:
        """Получить модули пользователя"""
        module_ids = self._user_modules.get(user_id, [])
        return [self._modules[mid] for mid in module_ids if mid in self._modules]

# Глобальный реестр
module_registry = ModuleRegistry()
