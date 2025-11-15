"""
Система достижений
"""
from config import game_config


# Определение достижений для кликера
CLICKER_ACHIEVEMENTS = {
    10: ("first_10", "🎉 Отлично! Первые 10 кликов!"),
    50: ("first_50", "🔥 Wow! 50 кликов!"),
    100: ("first_100", "⭐ Невероятно! 100 кликов!"),
    200: ("first_200", "💪 Мощно! 200 кликов!"),
    500: ("first_500", "🚀 Космос! 500 кликов!"),
    1000: ("first_1000", "👑 Король кликов! 1000!"),
}


def check_clicker_achievements(clicks: int, previous_clicks: int = None) -> tuple[bool, str, str]:
    """
    Проверка достижений кликера
    
    Args:
        clicks: Текущее количество кликов
        previous_clicks: Предыдущее количество кликов (для проверки новых достижений)
        
    Returns:
        Кортеж (есть_достижение, id_достижения, сообщение)
    """
    # Проверяем конкретные достижения
    if clicks in CLICKER_ACHIEVEMENTS:
        achievement_id, message = CLICKER_ACHIEVEMENTS[clicks]
        return True, achievement_id, f"\n\n{message}"
    
    # Проверяем достижения каждые 100 кликов после 1000
    if clicks > 1000 and clicks % 100 == 0:
        if previous_clicks is None or clicks != previous_clicks:
            achievement_id = f"milestone_{clicks}"
            message = f"\n\n💎 Легенда! {clicks} кликов!"
            return True, achievement_id, message
    
    return False, "", ""


def get_achievement_message(achievement_id: str) -> str:
    """
    Получить сообщение о достижении по его ID
    
    Args:
        achievement_id: ID достижения
        
    Returns:
        Текст сообщения о достижении
    """
    for clicks, (aid, message) in CLICKER_ACHIEVEMENTS.items():
        if aid == achievement_id:
            return message
    
    # Для milestone достижений
    if achievement_id.startswith("milestone_"):
        clicks = achievement_id.split("_")[1]
        return f"💎 Легенда! {clicks} кликов!"
    
    return "🎯 Достижение разблокировано!"


def get_all_achievements() -> dict[str, str]:
    """
    Получить список всех доступных достижений
    
    Returns:
        Словарь {achievement_id: описание}
    """
    achievements = {}
    for clicks, (aid, message) in CLICKER_ACHIEVEMENTS.items():
        achievements[aid] = f"{clicks} кликов: {message}"
    return achievements
