"""
Миграция: Добавление полей maks_id и maks_username в таблицу users
"""

import sqlite3
import os

# Путь к БД
db_path = os.path.join(os.path.dirname(__file__), '../eidos.db')

def migrate():
    """Применить миграцию"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверить существуют ли поля
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Добавить maks_id если не существует
        if 'maks_id' not in columns:
            print("Добавление поля maks_id...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN maks_id INTEGER
            """)
            print("✅ Поле maks_id добавлено")
        else:
            print("⏭️  Поле maks_id уже существует")
        
        # Добавить maks_username если не существует
        if 'maks_username' not in columns:
            print("Добавление поля maks_username...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN maks_username VARCHAR
            """)
            print("✅ Поле maks_username добавлено")
        else:
            print("⏭️  Поле maks_username уже существует")
        
        # Создать уникальные индексы
        print("Создание уникальных индексов...")
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_maks_id 
                ON users(maks_id) WHERE maks_id IS NOT NULL
            """)
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_maks_username 
                ON users(maks_username) WHERE maks_username IS NOT NULL
            """)
            print("✅ Уникальные индексы созданы")
        except Exception as e:
            print(f"⚠️  Ошибка создания индексов: {e}")
        
        conn.commit()
        print("\n✅ Миграция успешно применена!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Ошибка миграции: {e}")
        raise
    
    finally:
        conn.close()


def rollback():
    """Откатить миграцию (для SQLite сложно, нужно пересоздавать таблицу)"""
    print("⚠️  Откат миграции для SQLite требует пересоздания таблицы")
    print("Рекомендуется сделать бэкап БД перед миграцией")


if __name__ == "__main__":
    print("🔄 Запуск миграции: Добавление MAKS полей")
    print(f"📁 База данных: {db_path}")
    print()
    
    migrate()
