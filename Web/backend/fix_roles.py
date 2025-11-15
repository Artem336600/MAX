"""
Скрипт для исправления ролей пользователей в БД
"""
import sqlite3

# Подключение к БД
conn = sqlite3.connect('eidos.db')
cursor = conn.cursor()

# Обновить все роли на заглавные
cursor.execute("UPDATE users SET role = 'USER' WHERE role = 'user'")
cursor.execute("UPDATE users SET role = 'ADMIN' WHERE role = 'admin'")

# Сохранить изменения
conn.commit()

# Проверить результат
cursor.execute("SELECT id, email, role FROM users")
users = cursor.fetchall()

print("Обновлено пользователей:")
for user in users:
    print(f"  {user[1]}: {user[2]}")

conn.close()
print("\n✅ Роли обновлены!")
