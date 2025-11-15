"""
HTTP сервер модуля Workout Analyzer
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uvicorn
from datetime import datetime

from models.workout import Workout, Exercise
from analytics.stats import WorkoutStats
from ai.recommendations import WorkoutRecommendations

# API ключ модуля
API_KEY = "eidos_module_9moi12CsFV8kY12jWxvqARau7KRhVGqTcxW2mERF29k"

app = FastAPI(
    title="Workout Analyzer",
    version="1.0.0",
    description="Продвинутый анализатор тренировок с AI рекомендациями"
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище тренировок (в реальности будет БД)
workouts_storage = {}

def verify_api_key(x_eidos_module_key: Optional[str] = Header(None)):
    """Проверка API ключа"""
    if x_eidos_module_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "module": "Workout Analyzer",
        "version": "1.0.0"
    }

@app.get("/manifest")
async def manifest():
    """Манифест модуля"""
    return {
        "name": "Workout Analyzer",
        "version": "1.0.0",
        "description": "Продвинутый анализ тренировок с AI рекомендациями",
        "author": "Eidos Team",
        "permissions": ["database", "notifications"],
        "pages": [
            {
                "title": "Тренировки",
                "icon": "🏋️",
                "path": "/dashboard/workouts",
                "order": 20
            }
        ],
        "functions": [
            {
                "name": "add_workout",
                "description": "Добавить тренировку",
                "endpoint": "/workout/add"
            },
            {
                "name": "get_stats",
                "description": "Получить статистику тренировок",
                "endpoint": "/stats"
            },
            {
                "name": "get_recommendations",
                "description": "Получить AI рекомендации",
                "endpoint": "/recommendations"
            },
            {
                "name": "analyze_progress",
                "description": "Анализ прогресса по упражнению",
                "endpoint": "/progress"
            }
        ]
    }

@app.post("/message")
async def handle_message(
    data: dict,
    authorized: bool = Header(None, alias="x-eidos-module-key", convert_underscores=False)
):
    """Обработка сообщений от ИИ"""
    verify_api_key(authorized)
    
    user_id = data.get('user_id')
    message = data.get('data', {}).get('message', '')
    
    # Получить тренировки пользователя
    user_workouts = workouts_storage.get(user_id, [])
    
    if not user_workouts:
        return {
            "response": "У вас пока нет записанных тренировок. Добавьте первую тренировку, чтобы я мог проанализировать ваш прогресс!"
        }
    
    # Генерация ответа на основе сообщения
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['статистика', 'stats', 'прогресс']):
        stats = WorkoutStats.calculate_weekly_volume(user_workouts)
        frequency = WorkoutStats.calculate_frequency(user_workouts)
        
        response = f"📊 **Статистика тренировок**\n\n"
        response += f"Всего тренировок: {len(user_workouts)}\n\n"
        response += "**Объем по группам:**\n"
        for group, volume in stats.items():
            response += f"- {group}: {volume:.0f} кг\n"
        
        return {"response": response}
    
    elif any(word in message_lower for word in ['рекомендации', 'recommendations', 'совет']):
        recs = WorkoutRecommendations.generate_recommendations(user_workouts)
        
        response = "💡 **Рекомендации**\n\n"
        for rec in recs['recommendations'][:3]:
            response += f"**{rec['title']}**\n{rec['description']}\n\n"
        
        return {"response": response}
    
    elif any(word in message_lower for word in ['следующая', 'next', 'что тренировать']):
        suggestion = WorkoutRecommendations.suggest_next_workout(user_workouts)
        
        response = f"🎯 **Следующая тренировка**\n\n"
        response += f"**{suggestion['title']}**\n"
        response += f"{suggestion['description']}\n"
        
        return {"response": response}
    
    return {
        "response": "Я могу помочь вам с анализом тренировок! Спросите меня о статистике, рекомендациях или следующей тренировке."
    }

@app.post("/workout/add")
async def add_workout(
    data: dict,
    authorized: bool = Header(None, alias="x-eidos-module-key", convert_underscores=False)
):
    """Добавить тренировку"""
    verify_api_key(authorized)
    
    user_id = data.get('user_id')
    workout_data = data.get('data', {})
    
    # Создать тренировку
    workout = Workout(**workout_data)
    
    if user_id not in workouts_storage:
        workouts_storage[user_id] = []
    
    workouts_storage[user_id].append(workout)
    
    return {
        "success": True,
        "message": "Тренировка добавлена",
        "workout_id": workout.id
    }

@app.post("/stats")
async def get_stats(
    data: dict,
    authorized: bool = Header(None, alias="x-eidos-module-key", convert_underscores=False)
):
    """Получить статистику"""
    verify_api_key(authorized)
    
    user_id = data.get('user_id')
    user_workouts = workouts_storage.get(user_id, [])
    
    if not user_workouts:
        return {"error": "No workouts found"}
    
    volume = WorkoutStats.calculate_weekly_volume(user_workouts)
    frequency = WorkoutStats.calculate_frequency(user_workouts)
    intensity = WorkoutStats.calculate_intensity_trend(user_workouts)
    imbalances = WorkoutStats.detect_imbalances(user_workouts)
    
    return {
        "total_workouts": len(user_workouts),
        "volume_by_group": volume,
        "frequency_by_group": frequency,
        "intensity_trend": intensity,
        "imbalances": imbalances
    }

@app.post("/recommendations")
async def get_recommendations(
    data: dict,
    authorized: bool = Header(None, alias="x-eidos-module-key", convert_underscores=False)
):
    """Получить рекомендации"""
    verify_api_key(authorized)
    
    user_id = data.get('user_id')
    user_goal = data.get('data', {}).get('goal', 'general')
    user_workouts = workouts_storage.get(user_id, [])
    
    recs = WorkoutRecommendations.generate_recommendations(user_workouts, user_goal)
    next_workout = WorkoutRecommendations.suggest_next_workout(user_workouts)
    
    return {
        "recommendations": recs,
        "next_workout": next_workout
    }

@app.post("/progress")
async def analyze_progress(
    data: dict,
    authorized: bool = Header(None, alias="x-eidos-module-key", convert_underscores=False)
):
    """Анализ прогресса по упражнению"""
    verify_api_key(authorized)
    
    user_id = data.get('user_id')
    exercise_name = data.get('data', {}).get('exercise_name')
    user_workouts = workouts_storage.get(user_id, [])
    
    if not exercise_name:
        return {"error": "Exercise name required"}
    
    progress = WorkoutStats.calculate_progress(user_workouts, exercise_name)
    
    return progress

if __name__ == "__main__":
    print("=" * 60)
    print("🏋️  Workout Analyzer Module")
    print("=" * 60)
    print(f"\n🔑 API Key: {API_KEY}")
    print(f"📡 Starting server on http://0.0.0.0:8082")
    print(f"\n✅ Module is ready!\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8082)
