# Интеграция модулей и ИИ в Eidos

## 🧠 Как ИИ знает обо всех модулях

### Контекст ИИ

При каждом запросе пользователя ИИ получает **полный контекст**:

```json
{
  "user": {
    "id": "user_123",
    "name": "Артём",
    "preferences": {
      "sleep_goal": "8 hours",
      "budget_limit": 50000
    }
  },
  "installed_modules": [
    {
      "id": "sleep-tracker",
      "name": "Sleep Tracker",
      "description": "Отслеживает качество сна",
      "functions": [
        {
          "name": "record_sleep",
          "description": "Записать данные о сне",
          "parameters": {"quality": "number", "duration": "number"}
        },
        {
          "name": "get_stats",
          "description": "Получить статистику сна",
          "parameters": {"period": "string"}
        }
      ],
      "data_summary": {
        "last_sleep": {"quality": 8, "duration": 7.5},
        "avg_quality": 7.8,
        "trend": "improving"
      }
    },
    {
      "id": "finance-manager",
      "name": "Finance Manager",
      "description": "Управление финансами",
      "functions": [...],
      "data_summary": {
        "balance": 50000,
        "today_spent": 2000,
        "budget_status": "on_track"
      }
    }
  ],
  "conversation_history": [
    {"role": "user", "content": "Как я спал вчера?"},
    {"role": "assistant", "content": "Вчера ты спал 8/10..."}
  ]
}
```

### System Prompt для ИИ

```
Ты персональный ИИ-ассистент пользователя Артём.

У пользователя установлены следующие модули:

1. Sleep Tracker
   - Отслеживает качество сна (0-10) и длительность
   - Последний сон: 8/10, 7.5 часов
   - Средний за неделю: 7.8/10
   - Тренд: улучшается
   - Функции: record_sleep, get_stats, analyze_pattern

2. Finance Manager
   - Управляет финансами и бюджетом
   - Текущий баланс: 50,000₽
   - Сегодня потрачено: 2,000₽
   - Бюджет: в норме
   - Функции: add_transaction, get_balance, analyze_spending

3. Habit Tracker
   - Отслеживает привычки
   - Сегодня выполнено: 3/5
   - Текущий streak: 7 дней
   - Функции: log_habit, get_streaks

Когда пользователь задаёт вопрос:
1. Определи к какому модулю относится вопрос
2. Вызови нужную функцию модуля
3. Проанализируй данные из ВСЕХ модулей для персонализации
4. Дай полезный ответ с рекомендациями

Примеры:
- "Как я спал?" → вызови sleep_tracker.get_stats()
- "Сколько потратил?" → вызови finance_manager.get_balance()
- "Как мои привычки?" → вызови habit_tracker.get_streaks()

ВАЖНО: Анализируй данные из разных модулей вместе!
Например, если сон плохой И траты высокие → возможно стресс.
```

---

## 🔗 Интеграция между модулями

### 1. Публичный API модуля

Каждый модуль может предоставить **публичный API** для других модулей:

```python
# В манифесте модуля
public_api:
  - endpoint: /public/latest
    description: "Последняя запись о сне"
    returns: {quality: number, duration: number, date: string}
  
  - endpoint: /public/stats
    description: "Статистика за период"
    parameters: {period: string}
    returns: {avg_quality: number, avg_duration: number}
```

### 2. Запрос разрешений

Модуль запрашивает разрешение на доступ к другому модулю:

```yaml
# module.yaml для Health Dashboard
permissions:
  - modules:read:sleep-tracker
  - modules:read:fitness-tracker
  - modules:read:nutrition-tracker
```

### 3. Использование в коде

```python
# Health Dashboard может получать данные из других модулей
from eidos_sdk import ModuleAPI

class HealthDashboard(EidosModule):
    async def get_health_overview(self, user_id: str):
        # Получаем данные из Sleep Tracker
        sleep_data = await ModuleAPI.call(
            module_id="sleep-tracker",
            endpoint="/public/latest",
            user_id=user_id
        )
        
        # Получаем данные из Fitness Tracker
        fitness_data = await ModuleAPI.call(
            module_id="fitness-tracker",
            endpoint="/public/today",
            user_id=user_id
        )
        
        # Получаем данные из Nutrition Tracker
        nutrition_data = await ModuleAPI.call(
            module_id="nutrition-tracker",
            endpoint="/public/today",
            user_id=user_id
        )
        
        # Объединяем данные
        return {
            "sleep": sleep_data,
            "fitness": fitness_data,
            "nutrition": nutrition_data,
            "health_score": self._calculate_health_score(
                sleep_data, fitness_data, nutrition_data
            )
        }
    
    def _calculate_health_score(self, sleep, fitness, nutrition):
        """Комплексная оценка здоровья на основе всех данных"""
        score = 0
        
        # Сон (40% от оценки)
        if sleep['quality'] >= 8:
            score += 40
        elif sleep['quality'] >= 6:
            score += 30
        else:
            score += 20
        
        # Активность (30% от оценки)
        if fitness['steps'] >= 10000:
            score += 30
        elif fitness['steps'] >= 5000:
            score += 20
        else:
            score += 10
        
        # Питание (30% от оценки)
        if nutrition['calories'] <= nutrition['target']:
            score += 30
        else:
            score += 15
        
        return score
```

---

## 🎯 Персонализация ИИ

### Профиль пользователя

ИИ собирает данные из всех модулей для персонализации:

```python
class UserProfile:
    """Профиль пользователя на основе всех модулей"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.data = {}
    
    async def build_profile(self):
        """Собрать данные из всех модулей"""
        
        # Сон
        sleep_stats = await get_module_data("sleep-tracker", "stats")
        self.data['sleep'] = {
            'avg_quality': sleep_stats['avg_quality'],
            'avg_duration': sleep_stats['avg_duration'],
            'sleep_time': sleep_stats['usual_sleep_time'],
            'issues': self._detect_sleep_issues(sleep_stats)
        }
        
        # Финансы
        finance_stats = await get_module_data("finance-manager", "stats")
        self.data['finance'] = {
            'balance': finance_stats['balance'],
            'spending_pattern': finance_stats['pattern'],
            'stress_level': self._calculate_financial_stress(finance_stats)
        }
        
        # Привычки
        habits_stats = await get_module_data("habit-tracker", "stats")
        self.data['habits'] = {
            'completion_rate': habits_stats['completion_rate'],
            'streaks': habits_stats['streaks'],
            'motivation_level': self._calculate_motivation(habits_stats)
        }
        
        # Активность
        fitness_stats = await get_module_data("fitness-tracker", "stats")
        self.data['fitness'] = {
            'activity_level': fitness_stats['activity_level'],
            'workout_frequency': fitness_stats['frequency']
        }
        
        return self.data
    
    def get_insights(self):
        """Получить инсайты на основе всех данных"""
        insights = []
        
        # Корреляция сна и активности
        if self.data['sleep']['avg_quality'] < 7 and \
           self.data['fitness']['activity_level'] == 'low':
            insights.append({
                'type': 'correlation',
                'modules': ['sleep-tracker', 'fitness-tracker'],
                'message': 'Низкая активность может влиять на качество сна',
                'recommendation': 'Попробуй добавить больше физической активности'
            })
        
        # Корреляция финансов и стресса
        if self.data['finance']['stress_level'] == 'high' and \
           self.data['sleep']['avg_quality'] < 7:
            insights.append({
                'type': 'correlation',
                'modules': ['finance-manager', 'sleep-tracker'],
                'message': 'Финансовый стресс может влиять на сон',
                'recommendation': 'Рассмотри возможность оптимизации бюджета'
            })
        
        # Мотивация и привычки
        if self.data['habits']['motivation_level'] == 'low':
            insights.append({
                'type': 'motivation',
                'modules': ['habit-tracker'],
                'message': 'Мотивация снижается',
                'recommendation': 'Попробуй разбить большие цели на маленькие шаги'
            })
        
        return insights
```

### Пример работы ИИ с профилем

**Пользователь:** "Почему я так устал?"

**ИИ анализирует:**
1. Сон: качество 5/10 (низкое)
2. Активность: 2000 шагов (низкая)
3. Финансы: перерасход бюджета на 20%
4. Привычки: выполнено 1/5 (низкая мотивация)

**ИИ отвечает:**
```
Вижу несколько факторов:

🌙 Сон: Последние 3 дня качество сна низкое (5-6/10)
🏃 Активность: Всего 2000 шагов сегодня (норма 10000)
💰 Финансы: Перерасход бюджета на 20% - возможен стресс
✅ Привычки: Выполнено только 1/5 - мотивация снижается

Рекомендации:
1. Сегодня ляг пораньше (в 22:00)
2. Прогуляйся 30 минут - это поможет и со сном, и с настроением
3. Давай вместе посмотрим на бюджет и оптимизируем траты
4. Начни с одной простой привычки завтра

Хочешь, я напомню тебе лечь спать в 22:00?
```

---

## 🛠️ Для разработчиков модулей

### 1. Определение публичного API

```yaml
# module.yaml
name: "Sleep Tracker"
version: "1.0.0"

# Публичный API для других модулей
public_api:
  - endpoint: /public/latest
    method: GET
    description: "Последняя запись о сне"
    auth: module_token  # Требуется токен другого модуля
    returns:
      quality: number
      duration: number
      date: string
      notes: string
  
  - endpoint: /public/stats
    method: GET
    description: "Статистика за период"
    parameters:
      period: string  # week, month, year
    returns:
      avg_quality: number
      avg_duration: number
      trend: string
      best_day: object
      worst_day: object
  
  - endpoint: /public/subscribe
    method: POST
    description: "Подписаться на изменения"
    parameters:
      webhook_url: string
    returns:
      subscription_id: string
```

### 2. Реализация публичного API

```python
# api/public.py
from fastapi import APIRouter, Depends, HTTPException
from .auth import verify_module_token

router = APIRouter()

@router.get("/public/latest")
async def get_latest_sleep(
    user_id: str,
    requesting_module: str = Depends(verify_module_token),
    db: Session = Depends(get_db)
):
    """
    Публичный endpoint для других модулей
    Требует module_token для аутентификации
    """
    
    # Проверяем разрешения
    if not has_permission(requesting_module, user_id, "read"):
        raise HTTPException(403, "No permission")
    
    # Получаем последнюю запись
    record = db.query(SleepRecord)\
        .filter_by(user_id=user_id)\
        .order_by(SleepRecord.date.desc())\
        .first()
    
    if not record:
        return None
    
    return {
        "quality": record.quality,
        "duration": record.duration,
        "date": record.date.isoformat(),
        "notes": record.notes
    }

@router.get("/public/stats")
async def get_sleep_stats(
    user_id: str,
    period: str = "week",
    requesting_module: str = Depends(verify_module_token),
    db: Session = Depends(get_db)
):
    """Статистика за период"""
    
    if not has_permission(requesting_module, user_id, "read"):
        raise HTTPException(403, "No permission")
    
    stats = calculate_stats(user_id, period, db)
    return stats
```

### 3. Использование других модулей

```python
# В вашем модуле
from eidos_sdk import ModuleAPI, EidosModule

class HealthDashboard(EidosModule):
    def __init__(self, api_key: str):
        super().__init__(
            name="Health Dashboard",
            version="1.0.0",
            description="Комплексный дашборд здоровья",
            api_key=api_key
        )
        
        # Запрашиваем разрешения на чтение других модулей
        self.request_permissions([
            "modules:read:sleep-tracker",
            "modules:read:fitness-tracker",
            "modules:read:nutrition-tracker"
        ])
    
    async def get_health_overview(self, user_id: str):
        """Получить обзор здоровья из всех модулей"""
        
        # Используем ModuleAPI для вызова других модулей
        module_api = ModuleAPI(self.api_key)
        
        # Параллельные запросы к модулям
        sleep_data, fitness_data, nutrition_data = await asyncio.gather(
            module_api.call("sleep-tracker", "/public/latest", user_id),
            module_api.call("fitness-tracker", "/public/today", user_id),
            module_api.call("nutrition-tracker", "/public/today", user_id)
        )
        
        return {
            "sleep": sleep_data,
            "fitness": fitness_data,
            "nutrition": nutrition_data,
            "health_score": self._calculate_score(
                sleep_data, fitness_data, nutrition_data
            )
        }
```

### 4. Подписка на события других модулей

```python
class HabitTracker(EidosModule):
    async def on_install(self, user_id: str):
        """При установке подписываемся на события календаря"""
        
        # Подписываемся на создание событий в календаре
        await ModuleAPI.subscribe(
            module_id="calendar",
            event="event_created",
            webhook_url=f"{self.base_url}/webhooks/calendar",
            user_id=user_id
        )
    
    async def handle_calendar_event(self, event_data: dict):
        """Обработка события из календаря"""
        
        # Если создано событие "Тренировка"
        if "тренировка" in event_data['title'].lower():
            # Автоматически отмечаем привычку "Спорт"
            await self.log_habit(
                user_id=event_data['user_id'],
                habit_name="Спорт",
                auto=True
            )
```

---

## 🔄 События и Webhooks

### Система событий

Модули могут генерировать события, на которые подписываются другие модули:

```python
# Sleep Tracker генерирует событие
await self.emit_event(
    event_type="sleep_recorded",
    data={
        "quality": 8,
        "duration": 7.5,
        "date": "2025-11-15"
    }
)

# Health Dashboard подписан на это событие
@webhook("/webhooks/sleep")
async def on_sleep_recorded(self, event_data: dict):
    # Обновляем health score
    await self.update_health_score(event_data['user_id'])
```

### Типы событий

```python
# Стандартные события модулей
EVENTS = {
    "data_created": "Созданы новые данные",
    "data_updated": "Данные обновлены",
    "data_deleted": "Данные удалены",
    "goal_achieved": "Цель достигнута",
    "threshold_reached": "Достигнут порог",
    "pattern_detected": "Обнаружен паттерн"
}
```

---

## 🧩 Примеры интеграций

### 1. Sleep Tracker + Habit Tracker

```python
# Habit Tracker автоматически отмечает привычку "Хороший сон"
# когда Sleep Tracker фиксирует качество >= 8

@webhook("/webhooks/sleep")
async def on_sleep_recorded(self, event_data: dict):
    if event_data['quality'] >= 8:
        await self.log_habit(
            user_id=event_data['user_id'],
            habit_name="Хороший сон",
            auto=True
        )
```

### 2. Finance Manager + Mood Tracker

```python
# Mood Tracker анализирует корреляцию настроения и трат

async def analyze_mood_finance_correlation(self, user_id: str):
    # Получаем данные о тратах
    finance_data = await ModuleAPI.call(
        "finance-manager",
        "/public/stats",
        user_id,
        params={"period": "month"}
    )
    
    # Получаем данные о настроении
    mood_data = await self.get_mood_stats(user_id, period="month")
    
    # Анализируем корреляцию
    if finance_data['spending'] > finance_data['budget'] * 1.2:
        if mood_data['avg_mood'] < 5:
            return {
                "correlation": "high",
                "insight": "Перерасход бюджета коррелирует с низким настроением",
                "recommendation": "Рассмотри оптимизацию трат для снижения стресса"
            }
```

### 3. Study Assistant + Calendar + Habit Tracker

```python
# Study Assistant создаёт события в календаре
# и отмечает привычку "Учёба" в Habit Tracker

async def schedule_study_session(self, user_id: str, subject: str, date: str):
    # Создаём событие в календаре
    event = await ModuleAPI.call(
        "calendar",
        "/public/create_event",
        user_id,
        data={
            "title": f"Учёба: {subject}",
            "start": f"{date}T14:00:00",
            "end": f"{date}T16:00:00",
            "reminder": 30
        }
    )
    
    # Подписываемся на завершение события
    await ModuleAPI.subscribe(
        module_id="calendar",
        event=f"event_completed:{event['id']}",
        webhook_url=f"{self.base_url}/webhooks/study_completed"
    )

@webhook("/webhooks/study_completed")
async def on_study_completed(self, event_data: dict):
    # Отмечаем привычку "Учёба"
    await ModuleAPI.call(
        "habit-tracker",
        "/public/log_habit",
        event_data['user_id'],
        data={"habit_name": "Учёба", "completed": True}
    )
```

---

## 📊 Data Sharing Protocol

### Стандартный формат обмена данными

```json
{
  "module_id": "sleep-tracker",
  "user_id": "user_123",
  "data_type": "sleep_record",
  "timestamp": "2025-11-15T08:00:00Z",
  "data": {
    "quality": 8,
    "duration": 7.5,
    "sleep_time": "23:00",
    "wake_time": "06:30",
    "notes": "Хорошо выспался"
  },
  "metadata": {
    "source": "manual",  // manual, auto, imported
    "confidence": 1.0    // 0.0 - 1.0
  }
}
```

### Агрегированные данные

```json
{
  "module_id": "health-dashboard",
  "user_id": "user_123",
  "period": "week",
  "aggregated_data": {
    "sleep": {
      "avg_quality": 7.8,
      "avg_duration": 7.2,
      "trend": "improving"
    },
    "fitness": {
      "avg_steps": 8500,
      "workouts": 4,
      "trend": "stable"
    },
    "nutrition": {
      "avg_calories": 2100,
      "balance": "good"
    }
  },
  "health_score": 85,
  "insights": [
    "Сон улучшается",
    "Активность в норме",
    "Питание сбалансировано"
  ]
}
```

---

## 🎯 Итог для разработчиков

### Чек-лист интеграции модуля:

1. **Определи публичный API**
   - Какие данные можешь предоставить другим модулям?
   - Какие endpoints нужны?

2. **Запроси разрешения**
   - Какие модули тебе нужны?
   - Какой доступ требуется (read/write)?

3. **Реализуй интеграцию**
   - Используй ModuleAPI для вызова других модулей
   - Подпишись на нужные события

4. **Предоставь контекст для ИИ**
   - Опиши свои функции в манифесте
   - Предоставь data_summary для ИИ

5. **Тестируй интеграцию**
   - Проверь работу с другими модулями
   - Убедись что ИИ корректно использует твой модуль
