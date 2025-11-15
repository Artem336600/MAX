"""
Обработчики команд бота
"""
import aiomax
from aiomax import fsm

from config import messages
from keyboards import get_main_menu, get_clicker_keyboard, get_back_keyboard
from database import get_user_data, init_user_data
from utils import format_stats, format_clicker


def register_command_handlers(bot: aiomax.Bot):
    """
    Регистрация всех обработчиков команд
    
    Args:
        bot: Экземпляр бота
    """
    
    @bot.on_bot_start()
    async def on_start(pd: aiomax.BotStartPayload, cursor: fsm.FSMCursor):
        """Обработка нажатия кнопки 'Начать'"""
        init_user_data(cursor)
        await pd.send(messages.welcome, keyboard=get_main_menu())
    
    @bot.on_command('menu')
    async def menu_command(ctx: aiomax.CommandContext):
        """Команда /menu - показать главное меню"""
        await ctx.reply(messages.main_menu, keyboard=get_main_menu())
    
    @bot.on_command('stats')
    async def stats_command(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
        """Команда /stats - показать статистику"""
        user_data = get_user_data(cursor)
        stats_text = format_stats(user_data)
        await ctx.reply(stats_text, keyboard=get_back_keyboard())
    
    @bot.on_command('clicker')
    async def clicker_command(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
        """Команда /clicker - запустить кликер"""
        user_data = get_user_data(cursor)
        clicker_text = format_clicker(user_data.clicks)
        await ctx.reply(clicker_text, keyboard=get_clicker_keyboard())
    
    @bot.on_command('help')
    async def help_command(ctx: aiomax.CommandContext):
        """Команда /help - справка"""
        await ctx.reply(messages.help_text, keyboard=get_back_keyboard())
    
    @bot.on_command('start')
    async def start_command(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
        """Команда /start - перезапуск бота"""
        init_user_data(cursor)
        await ctx.reply(messages.welcome, keyboard=get_main_menu())
