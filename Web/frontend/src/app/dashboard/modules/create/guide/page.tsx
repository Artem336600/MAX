'use client'

import { useState } from 'react'
import { Copy, Check, Download, Code, FileCode, Rocket } from 'lucide-react'

export default function ModuleDevelopmentGuidePage() {
  const [copiedSection, setCopiedSection] = useState<string | null>(null)

  const copyToClipboard = (text: string, section: string) => {
    navigator.clipboard.writeText(text)
    setCopiedSection(section)
    setTimeout(() => setCopiedSection(null), 2000)
  }

  const pythonServerCode = `"""
Пример HTTP сервера для модуля Eidos
Этот файл содержит базовую структуру модуля с комментариями
"""

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

# TODO: Замените на ваш API ключ из панели управления
API_KEY = "eidos_module_ВСТАВЬТЕ_ВАШ_КЛЮЧ_СЮДА"

# TODO: Укажите информацию о вашем модуле
MODULE_INFO = {
    "name": "Мой Модуль",  # Название модуля
    "version": "1.0.0",     # Версия
    "description": "Описание того, что делает модуль",  # Краткое описание
    "author": "Ваше Имя",   # Автор
}

# ============================================
# СОЗДАНИЕ ПРИЛОЖЕНИЯ
# ============================================

app = FastAPI(
    title=MODULE_INFO["name"],
    version=MODULE_INFO["version"],
    description=MODULE_INFO["description"]
)

# Добавляем CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# МОДЕЛИ ДАННЫХ
# ============================================

class MessageRequest(BaseModel):
    """Запрос от ИИ к модулю"""
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    """Ответ модуля ИИ"""
    response: str
    data: Optional[Dict[str, Any]] = None

# TODO: Добавьте свои модели данных здесь
class MyCustomData(BaseModel):
    """Пример пользовательской модели"""
    field1: str
    field2: int
    # Добавьте нужные поля

# ============================================
# ОБЯЗАТЕЛЬНЫЕ ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """
    Проверка работоспособности модуля
    Eidos периодически вызывает этот endpoint
    """
    return {
        "status": "ok",
        "module": MODULE_INFO["name"],
        "version": MODULE_INFO["version"]
    }

@app.get("/manifest")
async def get_manifest():
    """
    Манифест модуля - описание возможностей
    Eidos использует это для интеграции с ИИ
    """
    return {
        "name": MODULE_INFO["name"],
        "version": MODULE_INFO["version"],
        "description": MODULE_INFO["description"],
        "author": MODULE_INFO["author"],
        
        # TODO: Опишите функции, которые ИИ может вызывать
        "functions": [
            {
                "name": "my_function",  # Имя функции
                "description": "Что делает эта функция",  # Описание для ИИ
                "parameters": {
                    "param1": {
                        "type": "string",
                        "description": "Описание параметра"
                    },
                    # Добавьте другие параметры
                },
                "endpoint": "/my-function"  # Куда отправлять запрос
            },
            # Добавьте другие функции
        ],
        
        # TODO: Если у модуля есть UI, опишите страницы
        "pages": [
            {
                "title": "Название страницы",
                "icon": "📊",  # Emoji иконка
                "path": "/dashboard/my-module",  # Путь в приложении
                "order": 100  # Порядок отображения
            }
        ],
        
        # Разрешения, которые нужны модулю
        "permissions": [
            "database",      # Доступ к БД пользователя
            "notifications", # Отправка уведомлений
            "calendar"       # Доступ к календарю
        ]
    }

@app.post("/message")
async def handle_message(
    request: MessageRequest,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Обработка сообщений от ИИ
    Вызывается когда ИИ решает использовать ваш модуль
    """
    
    # Проверка API ключа
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # TODO: Обработайте сообщение от ИИ
    user_message = request.message
    user_id = request.user_id
    
    # Пример обработки
    response_text = f"Модуль получил сообщение: {user_message}"
    
    # TODO: Добавьте вашу логику обработки
    # Например:
    # - Анализ данных
    # - Генерация рекомендаций
    # - Сохранение информации
    
    return MessageResponse(
        response=response_text,
        data={
            "processed": True,
            # Добавьте дополнительные данные
        }
    )

# ============================================
# ПОЛЬЗОВАТЕЛЬСКИЕ ENDPOINTS
# ============================================

# TODO: Добавьте свои endpoints здесь

@app.post("/my-function")
async def my_custom_function(
    data: MyCustomData,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Пример пользовательской функции
    ИИ может вызывать эту функцию
    """
    
    # Проверка API ключа
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # TODO: Реализуйте логику функции
    result = {
        "success": True,
        "message": "Функция выполнена успешно",
        "data": {
            # Верните результат
        }
    }
    
    return result

@app.get("/data/{user_id}")
async def get_user_data(
    user_id: str,
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Получение данных пользователя
    """
    
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # TODO: Получите и верните данные пользователя
    return {
        "user_id": user_id,
        "data": {
            # Данные пользователя
        }
    }

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

# TODO: Добавьте вспомогательные функции

def process_data(data: Any) -> Any:
    """
    Пример вспомогательной функции
    """
    # Ваша логика обработки
    return data

def analyze_user_behavior(user_id: str) -> Dict[str, Any]:
    """
    Анализ поведения пользователя
    """
    # TODO: Реализуйте анализ
    return {
        "insights": [],
        "recommendations": []
    }

# ============================================
# ЗАПУСК СЕРВЕРА
# ============================================

if __name__ == "__main__":
    # TODO: Измените порт если нужно
    PORT = 8080
    
    print(f"🚀 Запуск модуля '{MODULE_INFO['name']}'")
    print(f"📡 Сервер доступен на http://localhost:{PORT}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print(f"📖 Документация: http://localhost:{PORT}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
`

  const requirementsCode = `# Зависимости для Python модуля
# Установите командой: pip install -r requirements.txt

# Основной фреймворк
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Валидация данных
pydantic==2.5.0

# HTTP клиент (для запросов к Eidos API)
httpx==0.25.1
aiohttp==3.9.1

# TODO: Добавьте свои зависимости
# Например:
# numpy==1.24.3
# pandas==2.0.3
# scikit-learn==1.3.0
`

  const nodeServerCode = `/**
 * Пример HTTP сервера для модуля Eidos (Node.js)
 * Альтернатива Python версии
 */

const express = require('express');
const cors = require('cors');

// ============================================
// КОНФИГУРАЦИЯ
// ============================================

// TODO: Замените на ваш API ключ
const API_KEY = 'eidos_module_ВСТАВЬТЕ_ВАШ_КЛЮЧ_СЮДА';

const MODULE_INFO = {
  name: 'Мой Модуль',
  version: '1.0.0',
  description: 'Описание модуля',
  author: 'Ваше Имя'
};

// ============================================
// СОЗДАНИЕ ПРИЛОЖЕНИЯ
// ============================================

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Проверка API ключа
const checkApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  if (apiKey !== API_KEY) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  next();
};

// ============================================
// ОБЯЗАТЕЛЬНЫЕ ENDPOINTS
// ============================================

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    module: MODULE_INFO.name,
    version: MODULE_INFO.version
  });
});

app.get('/manifest', (req, res) => {
  res.json({
    ...MODULE_INFO,
    functions: [
      {
        name: 'my_function',
        description: 'Описание функции',
        parameters: {
          param1: {
            type: 'string',
            description: 'Описание параметра'
          }
        },
        endpoint: '/my-function'
      }
    ],
    pages: [
      {
        title: 'Моя страница',
        icon: '📊',
        path: '/dashboard/my-module',
        order: 100
      }
    ],
    permissions: ['database', 'notifications']
  });
});

app.post('/message', checkApiKey, (req, res) => {
  const { user_id, message, context } = req.body;
  
  // TODO: Обработайте сообщение
  
  res.json({
    response: \`Модуль получил: \${message}\`,
    data: {
      processed: true
    }
  });
});

// ============================================
// ПОЛЬЗОВАТЕЛЬСКИЕ ENDPOINTS
// ============================================

// TODO: Добавьте свои endpoints

app.post('/my-function', checkApiKey, (req, res) => {
  // Ваша логика
  res.json({
    success: true,
    message: 'Функция выполнена'
  });
});

// ============================================
// ЗАПУСК СЕРВЕРА
// ============================================

const PORT = process.env.PORT || 8080;

app.listen(PORT, () => {
  console.log(\`🚀 Запуск модуля '\${MODULE_INFO.name}'\`);
  console.log(\`📡 Сервер доступен на http://localhost:\${PORT}\`);
  console.log(\`🔑 API Key: \${API_KEY.substring(0, 20)}...\`);
});
`

  const packageJsonCode = `{
  "name": "my-eidos-module",
  "version": "1.0.0",
  "description": "Мой модуль для Eidos",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
`

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Code className="w-10 h-10 text-purple-600" />
          <h1 className="text-4xl font-bold text-gray-900">
            Руководство разработчика
          </h1>
        </div>
        <p className="text-xl text-gray-600">
          Полное руководство по созданию модулей для Eidos с примерами кода
        </p>
      </div>

      {/* Quick Start */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl border-2 border-purple-200 p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">🚀 Быстрый старт</h2>
        <ol className="space-y-3 text-gray-700">
          <li className="flex items-start gap-3">
            <span className="font-bold text-purple-600">1.</span>
            <span>Скопируйте код сервера ниже (Python или Node.js)</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="font-bold text-purple-600">2.</span>
            <span>Замените API_KEY на ваш ключ из панели управления</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="font-bold text-purple-600">3.</span>
            <span>Заполните TODO комментарии своей логикой</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="font-bold text-purple-600">4.</span>
            <span>Запустите сервер и протестируйте</span>
          </li>
        </ol>
      </div>

      {/* Python Example */}
      <div className="mb-8">
        <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileCode className="w-6 h-6 text-white" />
              <h3 className="text-xl font-bold text-white">server.py (Python + FastAPI)</h3>
            </div>
            <button
              onClick={() => copyToClipboard(pythonServerCode, 'python')}
              className="px-4 py-2 bg-white text-purple-600 rounded-lg hover:bg-gray-100 transition flex items-center gap-2"
            >
              {copiedSection === 'python' ? (
                <>
                  <Check className="w-4 h-4" />
                  Скопировано!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Копировать
                </>
              )}
            </button>
          </div>
          <div className="p-6 bg-gray-900 overflow-x-auto">
            <pre className="text-sm text-gray-100">
              <code>{pythonServerCode}</code>
            </pre>
          </div>
        </div>
      </div>

      {/* Requirements.txt */}
      <div className="mb-8">
        <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-green-600 to-teal-600 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileCode className="w-6 h-6 text-white" />
              <h3 className="text-xl font-bold text-white">requirements.txt</h3>
            </div>
            <button
              onClick={() => copyToClipboard(requirementsCode, 'requirements')}
              className="px-4 py-2 bg-white text-green-600 rounded-lg hover:bg-gray-100 transition flex items-center gap-2"
            >
              {copiedSection === 'requirements' ? (
                <>
                  <Check className="w-4 h-4" />
                  Скопировано!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Копировать
                </>
              )}
            </button>
          </div>
          <div className="p-6 bg-gray-900 overflow-x-auto">
            <pre className="text-sm text-gray-100">
              <code>{requirementsCode}</code>
            </pre>
          </div>
        </div>
      </div>

      {/* Node.js Example */}
      <div className="mb-8">
        <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-yellow-600 to-orange-600 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileCode className="w-6 h-6 text-white" />
              <h3 className="text-xl font-bold text-white">server.js (Node.js + Express)</h3>
            </div>
            <button
              onClick={() => copyToClipboard(nodeServerCode, 'node')}
              className="px-4 py-2 bg-white text-orange-600 rounded-lg hover:bg-gray-100 transition flex items-center gap-2"
            >
              {copiedSection === 'node' ? (
                <>
                  <Check className="w-4 h-4" />
                  Скопировано!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Копировать
                </>
              )}
            </button>
          </div>
          <div className="p-6 bg-gray-900 overflow-x-auto">
            <pre className="text-sm text-gray-100">
              <code>{nodeServerCode}</code>
            </pre>
          </div>
        </div>
      </div>

      {/* Package.json */}
      <div className="mb-8">
        <div className="bg-white rounded-xl border-2 border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-yellow-600 to-orange-600 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileCode className="w-6 h-6 text-white" />
              <h3 className="text-xl font-bold text-white">package.json</h3>
            </div>
            <button
              onClick={() => copyToClipboard(packageJsonCode, 'package')}
              className="px-4 py-2 bg-white text-orange-600 rounded-lg hover:bg-gray-100 transition flex items-center gap-2"
            >
              {copiedSection === 'package' ? (
                <>
                  <Check className="w-4 h-4" />
                  Скопировано!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Копировать
                </>
              )}
            </button>
          </div>
          <div className="p-6 bg-gray-900 overflow-x-auto">
            <pre className="text-sm text-gray-100">
              <code>{packageJsonCode}</code>
            </pre>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
          <Rocket className="w-7 h-7 text-purple-600" />
          Инструкции по запуску
        </h2>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-3">Python версия:</h3>
            <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-green-400">
              <div># Установите зависимости</div>
              <div>pip install -r requirements.txt</div>
              <div className="mt-2"># Запустите сервер</div>
              <div>python server.py</div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-3">Node.js версия:</h3>
            <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-green-400">
              <div># Установите зависимости</div>
              <div>npm install</div>
              <div className="mt-2"># Запустите сервер</div>
              <div>npm start</div>
            </div>
          </div>
        </div>
      </div>

      {/* Important Notes */}
      <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-6 mb-8">
        <h3 className="text-lg font-bold text-yellow-900 mb-4">⚠️ Важные замечания</h3>
        <ul className="space-y-2 text-yellow-800">
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Замените <code className="bg-yellow-100 px-2 py-1 rounded">API_KEY</code> на ваш реальный ключ</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Заполните все <code className="bg-yellow-100 px-2 py-1 rounded">TODO</code> комментарии</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Опишите функции в манифесте для интеграции с ИИ</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Добавьте обработку ошибок в production</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Используйте HTTPS в production окружении</span>
          </li>
        </ul>
      </div>

      {/* Next Steps */}
      <div className="bg-gradient-to-br from-green-50 to-teal-50 rounded-xl border-2 border-green-200 p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">✅ Следующие шаги</h2>
        <ol className="space-y-3 text-gray-700">
          <li className="flex items-start gap-3">
            <span className="font-bold text-green-600">1.</span>
            <span>Скопируйте код и создайте файлы</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="font-bold text-green-600">2.</span>
            <span>Установите зависимости</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="font-bold text-green-600">3.</span>
            <span>Запустите сервер локально</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="font-bold text-green-600">4.</span>
            <span>Протестируйте endpoints (откройте /docs для документации)</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="font-bold text-green-600">5.</span>
            <span>Добавьте свою логику в TODO местах</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="font-bold text-green-600">6.</span>
            <span>Опубликуйте модуль в Eidos</span>
          </li>
        </ol>

        <div className="mt-6 flex gap-4">
          <a
            href="/dashboard/modules/my"
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
          >
            Вернуться к модулям
          </a>
          <a
            href="/dashboard/chat"
            className="px-6 py-3 border-2 border-green-600 text-green-600 rounded-lg hover:bg-green-50 transition font-medium"
          >
            Спросить ИИ
          </a>
        </div>
      </div>
    </div>
  )
}
