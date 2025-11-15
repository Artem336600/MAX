# 📚 Руководство по разработке модулей для Eidos

Полное руководство по созданию модулей для платформы Eidos с примерами кода.

---

## 📖 Содержание

1. [Введение](#введение)
2. [Быстрый старт](#быстрый-старт)
3. [Структура модуля](#структура-модуля)
4. [Создание простого модуля](#создание-простого-модуля)
5. [Продвинутые функции](#продвинутые-функции)
6. [Публикация модуля](#публикация-модуля)
7. [Примеры](#примеры)

---

## 🎯 Введение

### Что такое модуль Eidos?

Модуль Eidos - это независимое приложение, которое расширяет функциональность платформы. Модули могут:

- 📊 Собирать и анализировать данные
- 🤖 Взаимодействовать с ИИ-ассистентом
- 🎨 Иметь собственный пользовательский интерфейс
- 🔔 Отправлять уведомления
- 📅 Создавать события в календаре

### Архитектура

```
┌─────────────┐         HTTP/Webhook        ┌──────────────┐
│             │ ◄──────────────────────────► │              │
│  Eidos Core │                              │ Ваш модуль   │
│             │ ◄──────────────────────────► │ (localhost)  │
└─────────────┘                              └──────────────┘
```

Ваш модуль работает как отдельный HTTP сервер, а Eidos отправляет ему запросы.

---

## 🚀 Быстрый старт

### Шаг 1: Установка зависимостей

```bash
# Python
pip install fastapi uvicorn

# Node.js
npm install express

# Go
go get github.com/gin-gonic/gin
```

### Шаг 2: Создание простейшего модуля

**Python (FastAPI):**

```python
from fastapi import FastAPI, Header
import uvicorn

app = FastAPI()

# Ваш API ключ (получите в Eidos)
API_KEY = "eidos_module_YOUR_KEY_HERE"

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "module": "My First Module",
        "version": "1.0.0"
    }

@app.get("/manifest")
async def manifest():
    """Информация о модуле"""
    return {
        "name": "My First Module",
        "version": "1.0.0",
        "description": "Мой первый модуль для Eidos",
        "functions": [
            {
                "name": "hello",
                "description": "Поздороваться с пользователем"
            }
        ]
    }

@app.post("/message")
async def handle_message(
    data: dict,
    x_eidos_module_key: str = Header(None)
):
    """Обработка сообщений от ИИ"""
    
    # Проверка API ключа
    if x_eidos_module_key != API_KEY:
        return {"error": "Invalid API key"}
    
    user_id = data.get('user_id')
    message = data.get('data', {}).get('message', '')
    
    return {
        "response": f"Привет! Вы написали: {message}"
    }

if __name__ == "__main__":
    print("🚀 Module started on http://localhost:8082")
    uvicorn.run(app, host="0.0.0.0", port=8082)
```

**Node.js (Express):**

```javascript
const express = require('express');
const app = express();

app.use(express.json());

const API_KEY = "eidos_module_YOUR_KEY_HERE";

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    module: 'My First Module',
    version: '1.0.0'
  });
});

app.get('/manifest', (req, res) => {
  res.json({
    name: 'My First Module',
    version: '1.0.0',
    description: 'Мой первый модуль для Eidos',
    functions: [
      {
        name: 'hello',
        description: 'Поздороваться с пользователем'
      }
    ]
  });
});

app.post('/message', (req, res) => {
  const apiKey = req.headers['x-eidos-module-key'];
  
  if (apiKey !== API_KEY) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  
  const { user_id, data } = req.body;
  const message = data?.message || '';
  
  res.json({
    response: `Привет! Вы написали: ${message}`
  });
});

app.listen(8082, () => {
  console.log('🚀 Module started on http://localhost:8082');
});
```

### Шаг 3: Запуск модуля

```bash
# Python
python server.py

# Node.js
node server.js
```

### Шаг 4: Регистрация в Eidos

1. Откройте Eidos → **Модули** → **Мои модули**
2. Нажмите **"Создать модуль"**
3. Следуйте мастеру создания:
   - Название: "My First Module"
   - Описание: "Мой первый модуль"
   - Webhook URL: `http://localhost:8082`
4. **Протестируйте** подключение
5. Создайте модуль

---

## 📁 Структура модуля

### Минимальная структура

```
my-module/
├── server.py          # Основной сервер
├── requirements.txt   # Зависимости
└── README.md         # Документация
```

### Продвинутая структура

```
my-module/
├── server.py              # HTTP сервер
├── requirements.txt       # Зависимости
├── README.md             # Документация
├── manifest.json         # Манифест модуля
├── models/               # Модели данных
│   └── data.py
├── handlers/             # Обработчики запросов
│   ├── messages.py
│   └── functions.py
├── utils/                # Утилиты
│   └── helpers.py
└── tests/                # Тесты
    └── test_module.py
```

---

## 🎨 Создание простого модуля

### Пример: Todo List модуль

**1. Создайте файл `todo_module.py`:**

```python
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime

app = FastAPI(title="Todo List Module")

API_KEY = "eidos_module_YOUR_KEY_HERE"

# Хранилище задач (в реальности используйте БД)
todos_storage = {}

class Todo(BaseModel):
    id: Optional[str] = None
    title: str
    completed: bool = False
    created_at: Optional[str] = None

def verify_api_key(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "module": "Todo List",
        "version": "1.0.0"
    }

@app.get("/manifest")
async def manifest():
    return {
        "name": "Todo List",
        "version": "1.0.0",
        "description": "Простой менеджер задач",
        "permissions": ["database", "notifications"],
        "functions": [
            {
                "name": "add_todo",
                "description": "Добавить задачу",
                "parameters": {
                    "title": {
                        "type": "string",
                        "description": "Название задачи"
                    }
                }
            },
            {
                "name": "list_todos",
                "description": "Показать все задачи"
            },
            {
                "name": "complete_todo",
                "description": "Отметить задачу как выполненную",
                "parameters": {
                    "id": {
                        "type": "string",
                        "description": "ID задачи"
                    }
                }
            }
        ]
    }

@app.post("/message")
async def handle_message(
    data: dict,
    x_eidos_module_key: str = Header(None)
):
    """Обработка сообщений от ИИ"""
    verify_api_key(x_eidos_module_key)
    
    user_id = data.get('user_id')
    message = data.get('data', {}).get('message', '').lower()
    
    # Получить задачи пользователя
    user_todos = todos_storage.get(user_id, [])
    
    if 'задач' in message or 'todo' in message:
        if not user_todos:
            return {"response": "У вас пока нет задач. Добавьте первую!"}
        
        response = "📝 Ваши задачи:\n\n"
        for i, todo in enumerate(user_todos, 1):
            status = "✅" if todo['completed'] else "⬜"
            response += f"{status} {i}. {todo['title']}\n"
        
        return {"response": response}
    
    return {
        "response": "Я могу помочь вам управлять задачами! Спросите 'покажи задачи' или используйте функции модуля."
    }

@app.post("/add_todo")
async def add_todo(
    data: dict,
    x_eidos_module_key: str = Header(None)
):
    """Добавить задачу"""
    verify_api_key(x_eidos_module_key)
    
    user_id = data.get('user_id')
    title = data.get('data', {}).get('title')
    
    if not title:
        return {"error": "Title is required"}
    
    # Создать задачу
    todo = {
        "id": str(len(todos_storage.get(user_id, [])) + 1),
        "title": title,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    
    if user_id not in todos_storage:
        todos_storage[user_id] = []
    
    todos_storage[user_id].append(todo)
    
    return {
        "success": True,
        "message": f"Задача '{title}' добавлена!",
        "todo": todo
    }

@app.post("/list_todos")
async def list_todos(
    data: dict,
    x_eidos_module_key: str = Header(None)
):
    """Список задач"""
    verify_api_key(x_eidos_module_key)
    
    user_id = data.get('user_id')
    user_todos = todos_storage.get(user_id, [])
    
    return {
        "todos": user_todos,
        "total": len(user_todos),
        "completed": len([t for t in user_todos if t['completed']])
    }

@app.post("/complete_todo")
async def complete_todo(
    data: dict,
    x_eidos_module_key: str = Header(None)
):
    """Отметить задачу выполненной"""
    verify_api_key(x_eidos_module_key)
    
    user_id = data.get('user_id')
    todo_id = data.get('data', {}).get('id')
    
    user_todos = todos_storage.get(user_id, [])
    
    for todo in user_todos:
        if todo['id'] == todo_id:
            todo['completed'] = True
            return {
                "success": True,
                "message": f"Задача '{todo['title']}' выполнена! 🎉"
            }
    
    return {"error": "Todo not found"}

if __name__ == "__main__":
    print("=" * 60)
    print("📝 Todo List Module")
    print("=" * 60)
    print(f"\n🔑 API Key: {API_KEY}")
    print(f"📡 Starting on http://localhost:8082\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8082)
```

**2. Создайте `requirements.txt`:**

```txt
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
```

**3. Запустите:**

```bash
pip install -r requirements.txt
python todo_module.py
```

---

## 🎨 Добавление UI в боковую панель

### В мастере создания модуля:

**Шаг 4: Пользовательский интерфейс**

1. ✅ Включите "Добавить пункт в боковую панель"
2. Заполните:
   - **Название в меню**: "Мои задачи"
   - **Иконка**: 📝
   - **URL путь**: `/dashboard/todos`
   - **Порядок**: 20

### В манифесте:

```json
{
  "name": "Todo List",
  "version": "1.0.0",
  "pages": [
    {
      "title": "Мои задачи",
      "icon": "📝",
      "path": "/dashboard/todos",
      "order": 20
    }
  ]
}
```

Теперь в боковой панели появится пункт "📝 Мои задачи"!

---

## 🔔 Отправка уведомлений

```python
import aiohttp

async def send_notification(user_id: str, title: str, message: str):
    """Отправить уведомление пользователю"""
    
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"http://localhost:8001/api/v1/modules/webhook/{API_KEY}",
            json={
                "action": "notify",
                "user_id": user_id,
                "title": title,
                "message": message,
                "priority": "normal"
            }
        )

# Использование
await send_notification(
    user_id="user123",
    title="Задача выполнена!",
    message="Вы выполнили задачу 'Купить молоко'"
)
```

---

## 📅 Создание событий в календаре

```python
async def create_calendar_event(user_id: str, title: str, start_time: str):
    """Создать событие в календаре"""
    
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"http://localhost:8001/api/v1/modules/webhook/{API_KEY}",
            json={
                "action": "create_event",
                "user_id": user_id,
                "title": title,
                "start_time": start_time,
                "duration": 60  # минуты
            }
        )
```

---

## 🚀 Публикация модуля

### 1. Создайте модуль

Используйте мастер создания модулей в Eidos.

### 2. Протестируйте

На шаге 3 мастера нажмите **"Запустить тест"** для проверки подключения.

### 3. Опубликуйте

1. Откройте **"Мои модули"**
2. Найдите свой модуль
3. Нажмите кнопку **📤 Upload**
4. Подтвердите публикацию

Модуль появится в маркетплейсе!

---

## 📚 Примеры модулей

### 1. Weather Module (Погода)

```python
import aiohttp

@app.post("/get_weather")
async def get_weather(data: dict, x_eidos_module_key: str = Header(None)):
    verify_api_key(x_eidos_module_key)
    
    city = data.get('data', {}).get('city', 'Moscow')
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=YOUR_KEY"
        ) as response:
            weather_data = await response.json()
    
    temp = weather_data['main']['temp'] - 273.15
    description = weather_data['weather'][0]['description']
    
    return {
        "city": city,
        "temperature": round(temp, 1),
        "description": description,
        "response": f"В городе {city} сейчас {round(temp, 1)}°C, {description}"
    }
```

### 2. Quote of the Day (Цитата дня)

```python
import random

QUOTES = [
    "Единственный способ сделать великую работу - любить то, что делаешь. - Стив Джобс",
    "Будущее принадлежит тем, кто верит в красоту своих мечтаний. - Элеонор Рузвельт",
    "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма. - Уинстон Черчилль"
]

@app.post("/quote")
async def get_quote(data: dict, x_eidos_module_key: str = Header(None)):
    verify_api_key(x_eidos_module_key)
    
    quote = random.choice(QUOTES)
    
    return {
        "quote": quote,
        "response": f"💭 {quote}"
    }
```

### 3. Pomodoro Timer

```python
from datetime import datetime, timedelta

pomodoro_sessions = {}

@app.post("/start_pomodoro")
async def start_pomodoro(data: dict, x_eidos_module_key: str = Header(None)):
    verify_api_key(x_eidos_module_key)
    
    user_id = data.get('user_id')
    duration = data.get('data', {}).get('duration', 25)  # минуты
    
    end_time = datetime.now() + timedelta(minutes=duration)
    pomodoro_sessions[user_id] = {
        "start": datetime.now().isoformat(),
        "end": end_time.isoformat(),
        "duration": duration
    }
    
    # Отправить уведомление через duration минут
    # (в реальности используйте планировщик задач)
    
    return {
        "success": True,
        "message": f"Pomodoro на {duration} минут запущен! 🍅",
        "end_time": end_time.isoformat()
    }
```

---

## 🔧 Отладка

### Логирование

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/message")
async def handle_message(data: dict, x_eidos_module_key: str = Header(None)):
    logger.info(f"Received message from user {data.get('user_id')}")
    logger.debug(f"Message data: {data}")
    
    # ... ваш код
```

### Тестирование локально

```bash
# Тест health endpoint
curl http://localhost:8082/health

# Тест message endpoint
curl -X POST http://localhost:8082/message \
  -H "Content-Type: application/json" \
  -H "X-Eidos-Module-Key: YOUR_API_KEY" \
  -d '{"user_id":"test","data":{"message":"hello"}}'
```

---

## 📖 Best Practices

### ✅ DO:

- Всегда проверяйте API ключ
- Обрабатывайте ошибки gracefully
- Логируйте важные события
- Документируйте функции
- Тестируйте перед публикацией

### ❌ DON'T:

- Не храните чувствительные данные в коде
- Не блокируйте event loop долгими операциями
- Не игнорируйте ошибки
- Не забывайте про безопасность

---

## 🆘 Помощь

### Частые проблемы

**Модуль не подключается:**
- Проверьте что сервер запущен
- Проверьте правильность URL
- Проверьте firewall

**Тест не проходит:**
- Убедитесь что `/health` endpoint работает
- Проверьте что порт не занят

**ИИ не видит модуль:**
- Проверьте что модуль опубликован (status: public)
- Перезапустите backend Eidos

### Контакты

- 📧 Email: support@eidos.dev
- 💬 Discord: discord.gg/eidos
- 📚 Docs: docs.eidos.dev

---

## 🎉 Готово!

Теперь вы знаете как создавать модули для Eidos! Начните с простого модуля и постепенно добавляйте функциональность.

**Удачи в разработке!** 🚀
