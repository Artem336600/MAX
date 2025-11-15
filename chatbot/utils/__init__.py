"""
Утилиты и вспомогательные функции
"""
from .formatters import format_stats, format_clicker, format_random_number
from .achievements import check_clicker_achievements, get_achievement_message

__all__ = [
    'format_stats',
    'format_clicker',
    'format_random_number',
    'check_clicker_achievements',
    'get_achievement_message'
]
