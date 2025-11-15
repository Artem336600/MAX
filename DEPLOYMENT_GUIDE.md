# 🚀 EIDOS - Руководство по развертыванию

## 📋 Содержание
- [Локальный запуск](#локальный-запуск)
- [Docker развертывание](#docker-развертывание)
- [Production развертывание](#production-развертывание)
- [Переменные окружения](#переменные-окружения)

---

## 🏠 Локальный запуск

### Требования
- Python 3.11+
- Node.js 18+
- MAKS Bot Token
- DeepSeek API Key

### Backend
```bash
cd Web/backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd Web/frontend
npm install
npm run dev
```

### Bot
```bash
cd chatbot
pip install -r requirements.txt
python bot_ai.py
```

---

## 🐳 Docker развертывание

### 1. Подготовка

Создайте `.env` файл:
```bash
cp .env.example .env
```

Заполните переменные:
```env
SECRET_KEY=your-super-secret-key-min-32-chars
DEEPSEEK_API_KEY=sk-your-deepseek-key
BOT_TOKEN=your-maks-bot-token
```

### 2. Сборка и запуск

```bash
# Сборка всех сервисов
docker-compose build

# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 3. Проверка

- Backend: http://localhost:8001/docs
- Frontend: http://localhost:3000
- Health: http://localhost:8001/health

---

## 🌐 Production развертывание

### VPS/Dedicated Server

#### 1. Установка Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin
```

#### 2. Клонирование проекта
```bash
git clone <your-repo>
cd OPTIMIZATION
```

#### 3. Настройка
```bash
# Создать .env
nano .env

# Установить переменные
SECRET_KEY=<strong-random-key>
DEEPSEEK_API_KEY=<your-key>
BOT_TOKEN=<your-token>
```

#### 4. Запуск
```bash
docker-compose up -d
```

#### 5. Настройка Nginx (опционально)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 6. SSL с Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🔐 Переменные окружения

### Backend
| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `SECRET_KEY` | JWT секретный ключ | `your-secret-key-change-in-production` |
| `DATABASE_URL` | URL базы данных | `sqlite+aiosqlite:///./eidos.db` |
| `ALGORITHM` | Алгоритм JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `10080` (7 дней) |

### Bot
| Переменная | Описание | Обязательно |
|-----------|----------|-------------|
| `DEEPSEEK_API_KEY` | API ключ DeepSeek | ✅ Да |
| `BOT_TOKEN` | Токен MAKS бота | ✅ Да |
| `SECRET_KEY` | JWT секретный ключ (тот же что и backend) | ✅ Да |
| `BACKEND_URL` | URL backend API | `http://backend:8001` |

### Frontend
| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `NEXT_PUBLIC_API_URL` | URL backend API | `http://localhost:8001` |

---

## 🔧 Обслуживание

### Бэкап базы данных
```bash
# Копирование БД
docker cp eidos-backend-1:/app/eidos.db ./backup/eidos_$(date +%Y%m%d).db

# Восстановление
docker cp ./backup/eidos.db eidos-backend-1:/app/eidos.db
docker-compose restart backend
```

### Обновление
```bash
# Остановка
docker-compose down

# Обновление кода
git pull

# Пересборка и запуск
docker-compose build
docker-compose up -d
```

### Логи
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f bot
docker-compose logs -f frontend
```

### Мониторинг
```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats
```

---

## 🐛 Troubleshooting

### Backend не запускается
```bash
# Проверить логи
docker-compose logs backend

# Проверить порты
netstat -tulpn | grep 8001

# Пересоздать контейнер
docker-compose up -d --force-recreate backend
```

### Bot не подключается
```bash
# Проверить переменные
docker-compose exec bot env | grep BOT_TOKEN

# Проверить логи
docker-compose logs bot

# Перезапустить
docker-compose restart bot
```

### Frontend ошибки
```bash
# Проверить логи
docker-compose logs frontend

# Пересобрать
docker-compose build frontend
docker-compose up -d frontend
```

---

## 📊 Архитектура

```
┌─────────────┐
│   Frontend  │ :3000
│  (Next.js)  │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
┌──────▼──────┐  ┌───▼────────┐
│   Backend   │  │  MAKS Bot  │
│  (FastAPI)  │  │  (aiomax)  │
└──────┬──────┘  └─────┬──────┘
       │               │
       └───────┬───────┘
               │
        ┌──────▼──────┐
        │   SQLite    │
        │  Database   │
        └─────────────┘
```

---

## 📝 Checklist перед деплоем

- [ ] Изменен `SECRET_KEY` на случайную строку
- [ ] Настроены переменные окружения
- [ ] Проверена работа всех сервисов локально
- [ ] Настроен firewall (порты 80, 443, 22)
- [ ] Настроен SSL сертификат
- [ ] Настроен автоматический бэкап БД
- [ ] Настроен мониторинг
- [ ] Проверена работа бота в MAKS

---

## 🎉 Готово!

Ваш EIDOS развернут и готов к работе!

**Полезные ссылки:**
- Backend API: http://your-domain.com/api
- Frontend: http://your-domain.com
- API Docs: http://your-domain.com/api/docs
- Health Check: http://your-domain.com/api/health

**Поддержка:**
- Документация: [README.md](README.md)
- Issues: GitHub Issues
