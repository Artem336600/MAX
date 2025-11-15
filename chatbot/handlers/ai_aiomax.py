"""
Обработчик AI сообщений для MAKS бота (aiomax)
"""

import sys
import os
import asyncio

# Добавить путь к ai_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import logging

from ai_core.engine import UnifiedAIEngine
from ai_core.tools import create_all_tools
from ai_core.context import ContextBuilder
from integrations.web_backend_simple import WebBackendIntegration
from config import bot_config

logger = logging.getLogger(__name__)

# Инициализация
ai_engine = UnifiedAIEngine(api_key=bot_config.deepseek_api_key if hasattr(bot_config, 'deepseek_api_key') else os.getenv('DEEPSEEK_API_KEY'))
web = WebBackendIntegration()
tools_manager = create_all_tools()

# История сообщений для каждого пользователя
user_histories = {}


def register_ai_handlers(bot):
    """Регистрация AI обработчиков"""
    
    @bot.on_command('/start')
    async def cmd_start(message):
        """Команда /start"""
        await message.reply(
            "👋 Привет! Я твой персональный ИИ-ассистент Eidos!\n\n"
            "Я помогу тебе управлять:\n"
            "🌙 Сном - отслеживание качества сна\n"
            "💪 Привычками - трекер целей\n"
            "💰 Финансами - управление бюджетом\n\n"
            "Просто напиши мне что-нибудь, например:\n"
            "• 'Я спал 8 часов, качество 9/10'\n"
            "• 'Создай привычку медитация каждый день'\n"
            "• 'Потратил 500 рублей на продукты'\n\n"
            "Команды:\n"
            "/stats - твоя статистика\n"
            "/help - помощь"
        )
    
    @bot.on_command('/stats')
    async def cmd_stats(message):
        """Команда /stats - показать статистику"""
        try:
            # Получить пользователя
            user_id = message.from_user.id if hasattr(message, 'from_user') else message.sender.id
            user_name = (message.from_user.name if hasattr(message, 'from_user') else 
                        message.sender.name if hasattr(message.sender, 'name') else "Пользователь")
            
            user = await web.get_or_create_user(
                maks_id=user_id,
                name=user_name
            )
            
            # Получить статистику
            sleep_stats = await web.get_sleep_stats(user.id)
            finance_stats = await web.get_finance_stats(user.id)
            habits = await web.get_habits(user.id)
            
            stats_text = "📊 **Твоя статистика:**\n\n"
            
            # Сон
            stats_text += f"🌙 **Сон:**\n"
            stats_text += f"• Записей: {sleep_stats['total_records']}\n"
            if sleep_stats['total_records'] > 0:
                stats_text += f"• Средняя длительность: {sleep_stats['avg_duration']}ч\n"
                stats_text += f"• Среднее качество: {sleep_stats['avg_quality']}/10\n"
            stats_text += "\n"
            
            # Привычки
            stats_text += f"💪 **Привычки:**\n"
            stats_text += f"• Активных: {len(habits)}\n"
            if habits:
                for habit in habits[:3]:
                    stats_text += f"  - {habit.icon} {habit.name}\n"
            stats_text += "\n"
            
            # Финансы
            stats_text += f"💰 **Финансы:**\n"
            stats_text += f"• Баланс: {finance_stats['balance']}₽\n"
            stats_text += f"• Доходы: {finance_stats['total_income']}₽\n"
            stats_text += f"• Расходы: {finance_stats['total_expense']}₽\n"
            
            await message.reply(stats_text)
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await message.reply("❌ Ошибка при получении статистики")
    
    @bot.on_command('/help')
    async def cmd_help(message):
        """Команда /help"""
        await message.reply(
            "❓ **Помощь**\n\n"
            "**Примеры команд:**\n\n"
            "🌙 **Сон:**\n"
            "• 'Я спал 8 часов, качество 9/10'\n"
            "• 'Проспал с 23:00 до 7:00'\n\n"
            "💪 **Привычки:**\n"
            "• 'Создай привычку медитация каждый день'\n"
            "• 'Я сделал медитацию'\n"
            "• 'Покажи мои привычки'\n\n"
            "💰 **Финансы:**\n"
            "• 'Потратил 500 на продукты'\n"
            "• 'Получил зарплату 50000'\n"
            "• 'Покажи баланс'\n\n"
            "**Команды:**\n"
            "/start - начать\n"
            "/stats - статистика\n"
            "/help - помощь"
        )
    
    @bot.on_message()
    async def handle_ai_message(message):
        """Обработка текстовых сообщений через ИИ"""
        
        # Получить текст сообщения (aiomax использует message.body)
        body = getattr(message, 'body', None)
        if body:
            # MessageBody может быть объектом, получаем текст
            text = getattr(body, 'text', None) or str(body)
        else:
            text = getattr(message, 'text', '')
        
        # Пропустить команды
        if text and isinstance(text, str) and text.startswith('/'):
            return
        
        # Пропустить пустые сообщения
        if not text or not isinstance(text, str):
            return
        
        try:
            # Получить или создать пользователя
            user_id = message.from_user.id if hasattr(message, 'from_user') else message.sender.id
            user_name = (message.from_user.name if hasattr(message, 'from_user') else 
                        message.sender.name if hasattr(message.sender, 'name') else "Пользователь")
            
            user = await web.get_or_create_user(
                maks_id=user_id,
                name=user_name
            )
            
            # Получить историю сообщений
            if user_id not in user_histories:
                user_histories[user_id] = []
            
            history = user_histories[user_id]
            
            # Создать system prompt
            system_prompt = ContextBuilder.build_system_prompt(
                user_name=user_name
            )
            
            # Подготовить сообщения
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history[-10:])  # Последние 10 сообщений
            messages.append({"role": "user", "content": text})
            
            # Получить инструменты
            tools = tools_manager.get_all()
            
            # Функция для выполнения инструментов
            async def tool_executor(function_name: str, arguments: dict):
                logger.info(f"Executing tool: {function_name} with args: {arguments}")
                result = await web.execute_function(function_name, arguments, user.id)
                return result
            
            # Отправить в ИИ
            response = await ai_engine.chat_with_tools(
                messages=messages,
                tools=tools,
                tool_executor=tool_executor
            )
            
            # Сохранить в историю
            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": response})
            
            # Ограничить размер истории
            if len(history) > 20:
                history = history[-20:]
            user_histories[user_id] = history
            
            # Отправить ответ
            await message.reply(response)
            
        except Exception as e:
            logger.error(f"Error handling AI message: {e}", exc_info=True)
            await message.reply(
                "❌ Произошла ошибка при обработке сообщения.\n"
                "Попробуйте еще раз или используйте /help"
            )
