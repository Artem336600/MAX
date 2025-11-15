"""
Работа с данными пользователей
"""
from dataclasses import dataclass, asdict, field
from typing import Optional
from aiomax import fsm


@dataclass
class UserData:
    """Структура данных пользователя"""
    clicks: int = 0
    random_calls: int = 0
    messages_sent: int = 0
    total_score: int = 0
    achievements: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserData':
        """Создание из словаря"""
        if not data:
            return cls()
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def add_click(self) -> int:
        """Добавить клик"""
        self.clicks += 1
        self.total_score += 1
        return self.clicks
    
    def add_random_call(self) -> int:
        """Добавить вызов генератора случайных чисел"""
        self.random_calls += 1
        return self.random_calls
    
    def add_message(self) -> int:
        """Добавить отправленное сообщение"""
        self.messages_sent += 1
        return self.messages_sent
    
    def add_achievement(self, achievement: str) -> bool:
        """
        Добавить достижение
        
        Returns:
            True если достижение новое, False если уже было
        """
        if achievement not in self.achievements:
            self.achievements.append(achievement)
            return True
        return False
    
    def has_achievement(self, achievement: str) -> bool:
        """Проверить наличие достижения"""
        return achievement in self.achievements


def get_user_data(cursor: fsm.FSMCursor) -> UserData:
    """
    Получить данные пользователя из FSM
    
    Args:
        cursor: FSM курсор пользователя
        
    Returns:
        UserData объект с данными пользователя
    """
    data = cursor.get_data()
    return UserData.from_dict(data)


def update_user_data(cursor: fsm.FSMCursor, user_data: UserData) -> None:
    """
    Обновить данные пользователя в FSM
    
    Args:
        cursor: FSM курсор пользователя
        user_data: Объект с данными пользователя
    """
    cursor.change_data(user_data.to_dict())


def init_user_data(cursor: fsm.FSMCursor) -> UserData:
    """
    Инициализировать данные пользователя если их нет
    
    Args:
        cursor: FSM курсор пользователя
        
    Returns:
        UserData объект с данными пользователя
    """
    user_data = get_user_data(cursor)
    if cursor.get_data() is None:
        update_user_data(cursor, user_data)
    return user_data
