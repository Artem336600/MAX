"""
Форматирование сообщений
"""
from database.user_data import UserData
from config import messages


def format_stats(user_data: UserData) -> str:
    """
    Форматирование статистики пользователя
    
    Args:
        user_data: Данные пользователя
        
    Returns:
        Отформатированная строка со статистикой
    """
    return messages.stats_template.format(
        clicks=user_data.clicks,
        random_calls=user_data.random_calls,
        messages_sent=user_data.messages_sent
    )


def format_clicker(clicks: int, motivation: str = "") -> str:
    """
    Форматирование сообщения кликера
    
    Args:
        clicks: Количество кликов
        motivation: Дополнительное мотивирующее сообщение
        
    Returns:
        Отформатированная строка
    """
    base_message = messages.clicker_template.format(clicks=clicks)
    if motivation:
        return f"{base_message}{motivation}"
    return base_message


def format_random_number(number: int) -> str:
    """
    Форматирование сообщения со случайным числом
    
    Args:
        number: Случайное число
        
    Returns:
        Отформатированная строка с эмодзи
    """
    # Определяем эмодзи в зависимости от числа
    emoji = "🎲"
    if number == 100:
        emoji = "🎰 ДЖЕКПОТ!"
    elif number >= 90:
        emoji = "⭐"
    elif number >= 70:
        emoji = "✨"
    elif number <= 10:
        emoji = "😢"
    
    return messages.random_template.format(
        emoji=emoji,
        number=number
    )


def format_number_with_suffix(number: int) -> str:
    """
    Форматирование больших чисел с суффиксами (K, M, B)
    
    Args:
        number: Число для форматирования
        
    Returns:
        Отформатированная строка
    """
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)
