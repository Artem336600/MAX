"""
Обработчики callback кнопок
"""
import aiomax
from aiomax import fsm
import random

from config import messages, game_config
from keyboards import get_main_menu, get_clicker_keyboard, get_back_keyboard
from database import get_user_data, update_user_data
from utils import format_stats, format_clicker, format_random_number, check_clicker_achievements


def register_callback_handlers(bot: aiomax.Bot):
    """
    Регистрация всех обработчиков callback кнопок
    
    Args:
        bot: Экземпляр бота
    """
    
    @bot.on_button_callback('clicker')
    async def clicker_button(callback: aiomax.Callback, cursor: fsm.FSMCursor):
        """Обработка нажатия на кнопку 'Кликер'"""
        user_data = get_user_data(cursor)
        clicker_text = format_clicker(user_data.clicks)
        await callback.answer(text=clicker_text, keyboard=get_clicker_keyboard())
    
    @bot.on_button_callback('click')
    async def on_click(callback: aiomax.Callback, cursor: fsm.FSMCursor):
        """Обработка клика в кликере"""
        user_data = get_user_data(cursor)
        previous_clicks = user_data.clicks
        
        # Добавляем клик
        user_data.add_click()
        
        # Проверяем достижения
        has_achievement, achievement_id, motivation = check_clicker_achievements(
            user_data.clicks, 
            previous_clicks
        )
        
        if has_achievement:
            user_data.add_achievement(achievement_id)
        
        # Сохраняем данные
        update_user_data(cursor, user_data)
        
        # Формируем ответ
        clicker_text = format_clicker(user_data.clicks, motivation)
        await callback.answer(text=clicker_text, keyboard=get_clicker_keyboard())
    
    @bot.on_button_callback('random')
    async def random_button(callback: aiomax.Callback, cursor: fsm.FSMCursor):
        """Обработка нажатия на кнопку 'Случайное число'"""
        user_data = get_user_data(cursor)
        user_data.add_random_call()
        update_user_data(cursor, user_data)
        
        # Генерируем случайное число
        number = random.randint(game_config.random_min, game_config.random_max)
        random_text = format_random_number(number)
        
        await callback.answer(text=random_text, keyboard=get_back_keyboard())
    
    @bot.on_button_callback('stats')
    async def stats_button(callback: aiomax.Callback, cursor: fsm.FSMCursor):
        """Обработка нажатия на кнопку 'Статистика'"""
        user_data = get_user_data(cursor)
        stats_text = format_stats(user_data)
        await callback.answer(text=stats_text, keyboard=get_back_keyboard())
    
    @bot.on_button_callback('help')
    async def help_button(callback: aiomax.Callback):
        """Обработка нажатия на кнопку 'Помощь'"""
        await callback.answer(text=messages.help_text, keyboard=get_back_keyboard())
    
    @bot.on_button_callback('menu')
    async def menu_button(callback: aiomax.Callback):
        """Обработка нажатия на кнопку 'Назад в меню'"""
        await callback.answer(text=messages.main_menu, keyboard=get_main_menu())
