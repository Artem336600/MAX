"""
Обработчики текстовых сообщений
"""
import aiomax
from aiomax import fsm
import random

from database import get_user_data, update_user_data


def register_message_handlers(bot: aiomax.Bot):
    """
    Регистрация всех обработчиков сообщений
    
    Args:
        bot: Экземпляр бота
    """
    
    @bot.on_message()
    async def echo_handler(message: aiomax.Message, cursor: fsm.FSMCursor):
        """Эхо-режим: повторение сообщений пользователя"""
        user_data = get_user_data(cursor)
        user_data.add_message()
        update_user_data(cursor, user_data)
        
        # Разные варианты ответов для разнообразия
        responses = [
            f"💬 Вы написали: {message.content}",
            f"📝 Повторяю: {message.content}",
            f"🔄 Эхо: {message.content}",
            f"✍️ Получил сообщение: {message.content}"
        ]
        
        await message.reply(random.choice(responses))
