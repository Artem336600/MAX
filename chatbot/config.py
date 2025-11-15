"""
Конфигурация бота
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    """Конфигурация бота"""
    token: str
    default_format: str = "markdown"
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """Загрузка конфигурации из переменных окружения"""
        token = os.getenv('BOT_TOKEN', 'f9LHodD0cOKMptoK2QIqIZPwTC49OHCLNxPYbNK_fo53f2aBZcDMD0C50ypddLazfao7vgAmO3EFZW5cbwBL')
        return cls(
            token=token,
            default_format=os.getenv('BOT_FORMAT', 'markdown'),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )


@dataclass
class GameConfig:
    """Конфигурация игровых механик"""
    # Кликер
    clicker_milestones: list[int] = None
    
    # Случайные числа
    random_min: int = 1
    random_max: int = 100
    random_jackpot: int = 100
    random_high: int = 90
    random_medium: int = 70
    random_low: int = 10
    
    def __post_init__(self):
        if self.clicker_milestones is None:
            self.clicker_milestones = [10, 50, 100, 200, 500, 1000]


@dataclass
class Messages:
    """Текстовые сообщения бота"""
    # Приветствие
    welcome: str = (
        "👋 **Привет! Я многофункциональный бот для MAKS!**\n\n"
        "🎯 Что я умею:\n"
        "• 🎮 Кликер - нажимай и набирай очки\n"
        "• 🎲 Генератор случайных чисел\n"
        "• 📊 Статистика твоих действий\n"
        "• 💬 Эхо-режим - повторяю твои сообщения\n\n"
        "Выбери действие:"
    )
    
    # Меню
    main_menu: str = "📋 **Главное меню:**\n\nВыбери действие:"
    
    # Помощь
    help_text: str = (
        "ℹ️ **Справка по командам:**\n\n"
        "📋 /menu - главное меню\n"
        "📊 /stats - твоя статистика\n"
        "🎮 /clicker - запустить кликер\n"
        "🎲 /random - случайное число\n"
        "ℹ️ /help - эта справка\n\n"
        "Также можешь просто писать мне сообщения - я буду их повторять!"
    )
    
    # Статистика
    stats_template: str = (
        "📊 **Твоя статистика:**\n\n"
        "👆 Кликов: **{clicks}**\n"
        "🎲 Случайных чисел: **{random_calls}**\n"
        "💬 Сообщений отправлено: **{messages_sent}**"
    )
    
    # Кликер
    clicker_template: str = (
        "🎮 **Кликер**\n\n"
        "Твои клики: **{clicks}**\n"
        "Жми на кнопку!"
    )
    
    # Случайное число
    random_template: str = (
        "🎲 **Случайное число**\n\n"
        "{emoji} Твоё число: **{number}**\n\n"
        "Нажми ещё раз для нового числа!"
    )


# Глобальные экземпляры конфигурации
bot_config = BotConfig.from_env()
game_config = GameConfig()
messages = Messages()
