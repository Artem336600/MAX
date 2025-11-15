"""
Скрипт для публикации модуля Sleep Tracker в маркетплейс
"""

import requests
import json

# Конфигурация
BASE_URL = "http://localhost:8001/api/v1"

def login():
    """Войти и получить токен"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@test.com",
            "password": "123456"
        }
    )
    response.raise_for_status()
    return response.json()["token"]

def create_module(token):
    """Создать модуль Sleep Tracker"""
    
    manifest = {
        "name": "Sleep Tracker",
        "version": "1.0.0",
        "description": "Отслеживание качества сна и анализ паттернов",
        "permissions": ["database", "notifications", "calendar"],
        "schemas": [
            {
                "name": "sleep_records",
                "fields": {
                    "quality": "number",
                    "duration": "number",
                    "sleep_time": "datetime",
                    "wake_time": "datetime",
                    "notes": "string",
                    "mood": "string"
                }
            }
        ],
        "functions": [
            {
                "name": "record_sleep",
                "description": "Записать данные о сне пользователя",
                "endpoint": "/record",
                "parameters": {
                    "quality": {
                        "type": "number",
                        "description": "Качество сна от 0 до 10"
                    },
                    "duration": {
                        "type": "number",
                        "description": "Длительность сна в часах"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Заметки о сне"
                    }
                }
            },
            {
                "name": "get_sleep_stats",
                "description": "Получить статистику сна пользователя",
                "endpoint": "/stats",
                "parameters": {}
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/modules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Sleep Tracker",
            "description": "Отслеживание качества сна и анализ паттернов",
            "version": "1.0.0",
            "manifest": manifest
        }
    )
    response.raise_for_status()
    return response.json()

def publish_module(token, module_id):
    """Опубликовать модуль (сделать публичным)"""
    response = requests.put(
        f"{BASE_URL}/modules/{module_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "status": "public"
        }
    )
    response.raise_for_status()
    return response.json()

def main():
    print("=== Публикация модуля Sleep Tracker ===\n")
    
    try:
        # Шаг 1: Войти
        print("1️⃣ Вход в систему...")
        token = login()
        print("   ✅ Успешно!\n")
        
        # Шаг 2: Создать модуль
        print("2️⃣ Создание модуля...")
        module = create_module(token)
        print(f"   ✅ Модуль создан!")
        print(f"   📦 ID: {module['id']}")
        print(f"   🔑 API Key: {module['api_key']}")
        print(f"   📊 Статус: {module['status']}\n")
        
        # Шаг 3: Опубликовать
        print("3️⃣ Публикация модуля...")
        updated = publish_module(token, module['id'])
        print(f"   ✅ Модуль опубликован!")
        print(f"   📊 Новый статус: {updated['status']}\n")
        
        print("=" * 50)
        print("✅ Модуль успешно опубликован в маркетплейсе!")
        print("\nТеперь вы можете:")
        print("1. Увидеть модуль в маркетплейсе")
        print("2. Установить его")
        print("3. Использовать в чате с ИИ")
        print("\n🔗 http://localhost:3000/dashboard/modules")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка: {e}")
        if hasattr(e.response, 'text'):
            print(f"   Детали: {e.response.text}")

if __name__ == "__main__":
    main()
