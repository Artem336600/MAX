"""
Запуск миграций базы данных
"""

import sys
import os

# Добавить путь к migrations
sys.path.insert(0, os.path.dirname(__file__))

from migrations.add_maks_fields import migrate

if __name__ == "__main__":
    print("=" * 50)
    print("  МИГРАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 50)
    print()
    
    try:
        migrate()
        print()
        print("=" * 50)
        print("  ГОТОВО!")
        print("=" * 50)
    except Exception as e:
        print()
        print("=" * 50)
        print("  ОШИБКА!")
        print("=" * 50)
        print(f"  {e}")
        sys.exit(1)
