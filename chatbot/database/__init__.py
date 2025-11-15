"""
Модуль работы с данными пользователей
"""
from .user_data import UserData, get_user_data, update_user_data, init_user_data

__all__ = [
    'UserData',
    'get_user_data',
    'update_user_data',
    'init_user_data'
]
