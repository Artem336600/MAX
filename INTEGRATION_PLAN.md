# План интеграции MAKS бота с Web Backend

## 🎯 Цель
Пользователи управляют всеми модулями сайта через MAKS мессенджер.

## 📋 Задачи

### 1. Создать общий AI модуль
- Вынести логику ИИ из Web в общий модуль
- Поддержка function calling (tools)
- Интеграция с модулями

### 2. Интегрировать бота с Web Backend
- Подключить бота к БД Web
- Использовать существующие модели
- Доступ к функциям модулей

### 3. Убрать веб-чат
- Удалить страницу `/dashboard/chat`
- Удалить API endpoints чата
- Обновить навигацию

### 4. Добавить инструкции
- Как подключиться к боту
- Документация команд

## 🏗️ Архитектура

```
/OPTIMIZATION
├── ai_core/                    # Общий AI модуль
│   ├── __init__.py
│   ├── engine.py              # Единый AI engine
│   ├── tools.py               # Function calling
│   └── context.py             # RAG контекст
│
├── Web/
│   ├── backend/
│   │   ├── models/            # Модели БД (используются ботом)
│   │   ├── api/               # API (без chat.py)
│   │   └── core/
│   │       └── ai.py          # Использует ai_core
│   └── frontend/
│       └── app/dashboard/
│           └── (без chat/)    # Чат удален
│
└── chatbot/
    ├── bot.py                 # Использует ai_core
    ├── handlers/
    │   └── ai_handler.py      # Обработка сообщений с ИИ
    └── integrations/
        └── web_backend.py     # Интеграция с Web БД
```

## 🚀 Этапы реализации

### Этап 1: Создать ai_core модуль
1. Создать структуру папок
2. Перенести AI логику из Web
3. Адаптировать для использования в обоих проектах

### Этап 2: Интегрировать бота с Web
1. Подключить БД Web к боту
2. Создать обработчики для модулей
3. Реализовать function calling в боте

### Этап 3: Убрать веб-чат
1. Удалить frontend чат
2. Удалить backend chat API
3. Обновить навигацию

### Этап 4: Тестирование
1. Проверить работу бота
2. Проверить доступ к модулям
3. Проверить function calling

## 📝 Детали реализации

### ai_core/engine.py
```python
class UnifiedAIEngine:
    """Единый движок ИИ для Web и MAKS бота"""
    
    def __init__(self, api_key: str, db_session=None):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.db = db_session
    
    async def chat_with_tools(
        self,
        messages: List[Dict],
        user_id: str,
        tools: List[Dict] = None
    ) -> str:
        """Чат с поддержкой инструментов"""
        # Получить доступные функции
        if tools is None:
            tools = await self.get_available_tools(user_id)
        
        # Отправить в DeepSeek
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        # Обработать tool calls
        if response.choices[0].message.tool_calls:
            return await self.handle_tool_calls(
                response.choices[0].message.tool_calls,
                user_id
            )
        
        return response.choices[0].message.content
```

### chatbot/integrations/web_backend.py
```python
import sys
sys.path.append('../Web/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from models.user import User
from models.sleep_tracker import SleepRecord
from models.habit_tracker import Habit
# ... остальные модели

class WebBackendIntegration:
    """Интеграция MAKS бота с Web Backend"""
    
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url)
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """Получить пользователя по Telegram ID"""
        # Связать MAKS ID с User ID в БД
        pass
    
    async def create_sleep_record(self, user_id: str, data: dict):
        """Создать запись о сне"""
        async with AsyncSession(self.engine) as session:
            record = SleepRecord(
                user_id=user_id,
                **data
            )
            session.add(record)
            await session.commit()
```

### chatbot/handlers/ai_handler.py
```python
from aiogram import Router, F
from aiogram.types import Message
from ai_core.engine import UnifiedAIEngine
from integrations.web_backend import WebBackendIntegration

router = Router()
ai_engine = UnifiedAIEngine(api_key=config.DEEPSEEK_API_KEY)
web = WebBackendIntegration(db_url=config.WEB_DB_URL)

@router.message(F.text)
async def handle_ai_message(message: Message):
    """Обработка сообщений через ИИ"""
    
    # Получить пользователя Web
    user = await web.get_user_by_telegram_id(message.from_user.id)
    
    # История сообщений
    messages = [
        {"role": "system", "content": "Ты ИИ-ассистент..."},
        {"role": "user", "content": message.text}
    ]
    
    # Отправить в ИИ с доступом к функциям
    response = await ai_engine.chat_with_tools(
        messages=messages,
        user_id=user.id
    )
    
    await message.answer(response)
```

## 🗑️ Что удалить из Web

### Backend:
- ❌ `/api/chat.py` - API чата
- ❌ `/core/ai.py` - переместить в ai_core
- ❌ `/models/chat.py` - модели чата (если не нужны)

### Frontend:
- ❌ `/app/dashboard/chat/` - страница чата
- ❌ Ссылка на чат в навигации

## ✅ Что добавить

### В Web Frontend:
```tsx
// Вместо чата - инструкция по подключению к боту
<div className="bg-blue-50 rounded-xl p-6">
  <h2 className="text-xl font-bold mb-4">Управление через MAKS</h2>
  <p className="mb-4">
    Управляйте всеми модулями через мессенджер MAKS!
  </p>
  <a 
    href="https://max.ru/bot/your_bot_name" 
    className="btn btn-primary"
  >
    Открыть бота →
  </a>
</div>
```

### В chatbot:
- ✅ Интеграция с Web БД
- ✅ Обработчики для всех модулей
- ✅ Function calling
- ✅ Команды для управления

## 📊 Функции доступные в боте

Все те же функции что были в веб-чате:

### Sleep Tracker
- `/sleep` - статистика сна
- "Я спал 8 часов" - создать запись

### Habit Tracker
- `/habits` - список привычек
- "Создай привычку медитация" - создать
- "Я сделал медитацию" - отметить

### Finance Manager
- `/finance` - статистика
- "Потратил 500 на продукты" - добавить расход

### Calendar
- `/calendar` - события
- "Создай встречу завтра в 15:00" - создать событие

## 🎯 Результат

**Пользователь в MAKS:**
```
👤 Пользователь: Я спал 8 часов, качество 9/10

🤖 Бот: ✅ Записал! 8 часов сна с качеством 9/10 - отлично!
        Твоя средняя длительность теперь 7.5 часов.
        
        📊 Статистика за неделю:
        - Средняя длительность: 7.5ч
        - Среднее качество: 8.2/10
        - Лучший день: Суббота (9.5/10)
```

**Веб-сайт:**
- Показывает данные из БД
- Графики, статистика, аналитика
- Но без чата - только просмотр

---

**Начинаю реализацию?** 🚀
