"""
Генерация уникальных учетных данных для входа на сайт
"""

import secrets
import string
import hashlib


def generate_username(maks_id: int) -> str:
    """
    Генерация уникального логина на основе MAKS ID
    
    Args:
        maks_id: ID пользователя в MAKS
    
    Returns:
        Уникальный логин (например: eidos_abc123)
    """
    # Генерируем короткий хеш от ID
    hash_part = hashlib.md5(str(maks_id).encode()).hexdigest()[:6]
    return f"eidos_{hash_part}"


def generate_password(length: int = 12) -> str:
    """
    Генерация безопасного пароля
    
    Args:
        length: Длина пароля
    
    Returns:
        Случайный пароль
    """
    # Используем буквы, цифры и некоторые спецсимволы
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def generate_simple_password(length: int = 8) -> str:
    """
    Генерация простого пароля (только буквы и цифры)
    
    Args:
        length: Длина пароля
    
    Returns:
        Простой пароль
    """
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def hash_password(password: str) -> str:
    """
    Хеширование пароля для хранения в БД
    
    Args:
        password: Пароль в открытом виде
    
    Returns:
        Хеш пароля
    """
    # Простое хеширование (в продакшене использовать bcrypt)
    return hashlib.sha256(password.encode()).hexdigest()
