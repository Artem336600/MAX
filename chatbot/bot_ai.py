"""
AI бот для MAKS - простая версия
"""
import aiomax
import logging
import os
import sys
from sqlalchemy import select

# Добавить путь к ai_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_core.engine import UnifiedAIEngine
from ai_core.tools import create_all_tools
from ai_core.context import ContextBuilder
from integrations.web_backend_simple import User
from integrations.web_backend_simple import WebBackendIntegration
from config import bot_config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация
deepseek_key = os.getenv('DEEPSEEK_API_KEY')
if not deepseek_key:
    raise ValueError("DEEPSEEK_API_KEY not set! Use: $env:DEEPSEEK_API_KEY='your_key'")

ai_engine = UnifiedAIEngine(api_key=deepseek_key)
web = WebBackendIntegration()
tools_manager = create_all_tools()

# Логирование количества инструментов
logger.info(f"Загружено инструментов: {tools_manager.count()}")
logger.info(f"Список инструментов: {list(tools_manager.tools.keys())}")

# История сообщений
user_histories = {}


# Вспомогательная функция для обработки AI сообщений
async def handle_ai_message(pd, text):
    """Обработка сообщения через AI"""
    try:
        # Получить пользователя
        sender_id = getattr(pd.sender, 'user_id', None) or getattr(pd.sender, 'id', None)
        sender_name = getattr(pd.sender, 'name', None) or getattr(pd.sender, 'username', 'Пользователь')
        
        user, _ = await web.get_or_create_user(
            maks_id=sender_id,
            name=sender_name
        )
        
        # История
        user_id = sender_id
        if user_id not in user_histories:
            user_histories[user_id] = []
        
        history = user_histories[user_id]
        
        # System prompt
        system_prompt = ContextBuilder.build_system_prompt(
            user_name=sender_name
        )
        
        # Подготовить сообщения
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-10:])
        messages.append({"role": "user", "content": text})
        
        # Получить инструменты
        tools = tools_manager.get_all()
        
        # Функция для выполнения
        async def tool_executor(function_name: str, arguments: dict):
            logger.info(f"Executing: {function_name}")
            result = await web.execute_function(function_name, arguments, user.id)
            return result
        
        # Отправить в ИИ
        response = await ai_engine.chat_with_tools(
            messages=messages,
            tools=tools,
            tool_executor=tool_executor
        )
        
        # Сохранить историю
        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": response})
        
        if len(history) > 20:
            history = history[-20:]
        user_histories[user_id] = history
        
        # Отправить ответ
        await pd.send(response)
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await pd.send(
            "❌ Произошла ошибка при обработке сообщения.\n"
            "Попробуйте еще раз или используйте /help"
        )


# Создать бота
bot = aiomax.Bot(bot_config.token, default_format="markdown")


# ВАЖНО: Регистрируем команды ПЕРВЫМИ, чтобы они обрабатывались до on_message
@bot.on_command('/start')
async def on_start(pd):
    """Команда /start - выдает учетные данные для входа на сайт"""
    try:
        sender_id = getattr(pd.sender, 'user_id', None) or getattr(pd.sender, 'id', None)
        sender_name = getattr(pd.sender, 'name', None) or getattr(pd.sender, 'username', 'Пользователь')
        
        # Получить или создать пользователя
        user, password = await web.get_or_create_user(
            maks_id=sender_id,
            name=sender_name,
            generate_credentials=True
        )
        
        message = "👋 Привет! Я твой персональный ИИ-ассистент Eidos!\n\n"
        
        # Всегда показываем учетные данные
        message += "🔑 **Твои учетные данные для входа на сайт:**\n"
        message += f"• Логин: `{user.maks_username}`\n"
        
        if password:
            # Новый пользователь - показываем сгенерированный пароль
            message += f"• Пароль: `{password}`\n\n"
            message += "⚠️ **ВАЖНО! Сохрани пароль!**\n"
            message += "Пароль показывается только при первом запуске.\n"
        else:
            # Существующий пользователь - генерируем новый временный пароль для показа
            import sys
            import os
            utils_path = os.path.join(os.path.dirname(__file__), 'utils')
            if utils_path not in sys.path:
                sys.path.insert(0, utils_path)
            from credentials import generate_simple_password, hash_password
            
            # Генерируем новый пароль
            new_password = generate_simple_password(8)
            
            # Обновляем пароль в БД
            async with web.async_session() as session:
                result = await session.execute(
                    select(User).where(User.maks_id == sender_id)
                )
                db_user = result.scalar_one_or_none()
                if db_user:
                    db_user.password_hash = hash_password(new_password)
                    await session.commit()
            
            message += f"• Пароль: `{new_password}`\n\n"
            message += "� **Пароль обновлен!**\n"
            message += "Используй новый пароль для входа на сайт.\n"
        
        message += f"🌐 Сайт: http://localhost:3000/maks-login\n\n"
        
        message += (
            "Я помогу тебе управлять:\n"
            "🌙 Сном - отслеживание качества сна\n"
            "💪 Привычками - трекер целей\n"
            "💰 Финансами - управление бюджетом\n\n"
            "💬 Просто напиши мне что-нибудь:\n"
            "• Я спал 8 часов, качество 9/10\n"
            "• Создай привычку медитация каждый день\n"
            "• Потратил 500 рублей на продукты\n\n"
            "📋 Команды:\n"
            "/stats - твоя статистика\n"
            "/website - ссылка на сайт\n"
            "/credentials - показать логин\n"
            "/help - помощь"
        )
        
        await pd.send(message)
        
    except Exception as e:
        logger.error(f"Error in /start: {e}", exc_info=True)
        await pd.send("❌ Ошибка при создании учетной записи")


@bot.on_command('/credentials')
async def on_credentials(pd):
    """Команда /credentials - показать логин"""
    try:
        sender_id = getattr(pd.sender, 'user_id', None) or getattr(pd.sender, 'id', None)
        sender_name = getattr(pd.sender, 'name', None) or getattr(pd.sender, 'username', 'Пользователь')
        
        user, _ = await web.get_or_create_user(
            maks_id=sender_id,
            name=sender_name
        )
        
        message = "🔑 **Твои учетные данные:**\n\n"
        message += f"• Логин: `{user.maks_username}`\n"
        message += f"• Пароль: (был выдан при первом /start)\n\n"
        message += f"🌐 Сайт: http://localhost:3000\n\n"
        message += "💡 Используй эти данные для входа на сайт."
        
        await pd.send(message)
        
    except Exception as e:
        logger.error(f"Error in /credentials: {e}", exc_info=True)
        await pd.send("❌ Ошибка при получении учетных данных")


@bot.on_command('/stats')
async def on_stats(pd):
    """Команда /stats"""
    try:
        sender_id = getattr(pd.sender, 'user_id', None) or getattr(pd.sender, 'id', None)
        sender_name = getattr(pd.sender, 'name', None) or getattr(pd.sender, 'username', 'Пользователь')
        
        user, _ = await web.get_or_create_user(
            maks_id=sender_id,
            name=sender_name
        )
        
        sleep_stats = await web.get_sleep_stats(user.id)
        finance_stats = await web.get_finance_stats(user.id)
        habits = await web.get_habits(user.id)
        
        stats_text = "📊 **Твоя статистика:**\n\n"
        
        stats_text += f"🌙 **Сон:**\n"
        stats_text += f"• Записей: {sleep_stats['total_records']}\n"
        if sleep_stats['total_records'] > 0:
            stats_text += f"• Средняя длительность: {sleep_stats['avg_duration']}ч\n"
            stats_text += f"• Среднее качество: {sleep_stats['avg_quality']}/10\n"
        stats_text += "\n"
        
        stats_text += f"💪 **Привычки:**\n"
        stats_text += f"• Активных: {len(habits)}\n"
        if habits:
            for habit in habits[:3]:
                stats_text += f"  - {habit.icon} {habit.name}\n"
        stats_text += "\n"
        
        stats_text += f"💰 **Финансы:**\n"
        stats_text += f"• Баланс: {finance_stats['balance']}₽\n"
        stats_text += f"• Доходы: {finance_stats['total_income']}₽\n"
        stats_text += f"• Расходы: {finance_stats['total_expense']}₽\n"
        
        await pd.send(stats_text)
        
    except Exception as e:
        logger.error(f"Error in stats: {e}", exc_info=True)
        await pd.send("❌ Ошибка при получении статистики")


@bot.on_command('/help')
async def on_help(pd):
    """Команда /help"""
    await pd.send(
        "❓ **Помощь**\n\n"
        "**💬 Общение с AI:**\n"
        "Просто напиши мне обычным текстом:\n\n"
        "🌙 **Сон:**\n"
        "• Я спал 8 часов, качество 9/10\n"
        "• Проспал с 23:00 до 7:00\n\n"
        "💪 **Привычки:**\n"
        "• Создай привычку медитация каждый день\n"
        "• Я сделал медитацию\n"
        "• Покажи мои привычки\n\n"
        "💰 **Финансы:**\n"
        "• Потратил 500 на продукты\n"
        "• Получил зарплату 50000\n"
        "• Покажи баланс\n\n"
        "**📋 Команды:**\n"
        "/start - начать и получить учетные данные\n"
        "/stats - твоя статистика\n"
        "/website - ссылка на сайт\n"
        "/credentials - показать логин\n"
        "/sleep - статистика сна\n"
        "/habits - список привычек\n"
        "/finance - финансовая статистика\n"
        "/help - эта справка"
    )


@bot.on_command('/website')
async def on_website(pd):
    """Команда /website - ссылка на сайт"""
    try:
        sender_id = getattr(pd.sender, 'user_id', None) or getattr(pd.sender, 'id', None)
        sender_name = getattr(pd.sender, 'name', None) or getattr(pd.sender, 'username', 'Пользователь')
        
        user, _ = await web.get_or_create_user(
            maks_id=sender_id,
            name=sender_name
        )
        
        message = "🌐 **Веб-сайт Eidos**\n\n"
        message += "📊 Посмотри подробную статистику на сайте:\n"
        message += "🔗 http://localhost:3000/maks-login\n\n"
        message += "🔑 **Твои учетные данные:**\n"
        message += f"• Логин: `{user.maks_username}`\n"
        message += "• Пароль: (был выдан при /start)\n\n"
        message += "💡 На сайте ты найдешь:\n"
        message += "• 📈 Графики и аналитику\n"
        message += "• 📅 Календарь событий\n"
        message += "• 🎯 Детальную статистику\n"
        message += "• ⚙️ Настройки профиля"
        
        await pd.send(message)
        
    except Exception as e:
        logger.error(f"Error in /website: {e}", exc_info=True)
        await pd.send("❌ Ошибка при получении ссылки")


@bot.on_command('/sleep')
async def on_sleep(pd):
    """Команда /sleep - статистика сна"""
    try:
        sender_id = getattr(pd.sender, 'user_id', None) or getattr(pd.sender, 'id', None)
        sender_name = getattr(pd.sender, 'name', None) or getattr(pd.sender, 'username', 'Пользователь')
        
        user, _ = await web.get_or_create_user(
            maks_id=sender_id,
            name=sender_name
        )
        
        sleep_stats = await web.get_sleep_stats(user.id)
        
        message = "🌙 **Статистика сна:**\n\n"
        
        if sleep_stats['total_records'] == 0:
            message += "У тебя пока нет записей о сне.\n\n"
            message += "💡 Попробуй сказать:\n"
            message += "• 'Я спал 8 часов, качество 9/10'\n"
            message += "• 'Проспал с 23:00 до 7:00'"
        else:
            message += f"📊 Всего записей: {sleep_stats['total_records']}\n"
            message += f"⏰ Средняя длительность: {sleep_stats['avg_duration']}ч\n"
            message += f"⭐ Среднее качество: {sleep_stats['avg_quality']}/10\n"
            message += f"🏆 Лучшее качество: {sleep_stats['best_quality']}/10\n"
            message += f"📉 Худшее качество: {sleep_stats['worst_quality']}/10\n\n"
            message += "🌐 Подробнее на сайте: /website"
        
        await pd.send(message)
        
    except Exception as e:
        logger.error(f"Error in /sleep: {e}", exc_info=True)
        await pd.send("❌ Ошибка при получении статистики сна")


@bot.on_command('/habits')
async def on_habits(pd):
    """Команда /habits - список привычек"""
    try:
        sender_id = getattr(pd.sender, 'user_id', None) or getattr(pd.sender, 'id', None)
        sender_name = getattr(pd.sender, 'name', None) or getattr(pd.sender, 'username', 'Пользователь')
        
        user, _ = await web.get_or_create_user(
            maks_id=sender_id,
            name=sender_name
        )
        
        habits = await web.get_habits(user.id)
        
        message = "💪 **Твои привычки:**\n\n"
        
        if not habits:
            message += "У тебя пока нет привычек.\n\n"
            message += "💡 Попробуй сказать:\n"
            message += "• 'Создай привычку медитация каждый день'\n"
            message += "• 'Создай привычку зарядка 3 раза в неделю'"
        else:
            for habit in habits:
                message += f"{habit.icon} **{habit.name}**\n"
                message += f"   Частота: {habit.frequency}\n"
                if habit.description:
                    message += f"   {habit.description}\n"
                message += "\n"
            
            message += "🌐 Подробнее на сайте: /website"
        
        await pd.send(message)
        
    except Exception as e:
        logger.error(f"Error in /habits: {e}", exc_info=True)
        await pd.send("❌ Ошибка при получении привычек")


@bot.on_command('/finance')
async def on_finance(pd):
    """Команда /finance - финансовая статистика"""
    try:
        sender_id = getattr(pd.sender, 'user_id', None) or getattr(pd.sender, 'id', None)
        sender_name = getattr(pd.sender, 'name', None) or getattr(pd.sender, 'username', 'Пользователь')
        
        user, _ = await web.get_or_create_user(
            maks_id=sender_id,
            name=sender_name
        )
        
        finance_stats = await web.get_finance_stats(user.id)
        
        message = "💰 **Финансовая статистика:**\n\n"
        
        if finance_stats['transactions_count'] == 0:
            message += "У тебя пока нет транзакций.\n\n"
            message += "💡 Попробуй сказать:\n"
            message += "• 'Потратил 500 на продукты'\n"
            message += "• 'Получил зарплату 50000'"
        else:
            balance = finance_stats['balance']
            balance_emoji = "💚" if balance >= 0 else "❤️"
            
            message += f"{balance_emoji} **Баланс: {balance:,.0f}₽**\n\n"
            message += f"📈 Доходы: {finance_stats['total_income']:,.0f}₽\n"
            message += f"📉 Расходы: {finance_stats['total_expense']:,.0f}₽\n"
            message += f"📊 Транзакций: {finance_stats['transactions_count']}\n\n"
            message += "🌐 Подробнее на сайте: /website"
        
        await pd.send(message)
        
    except Exception as e:
        logger.error(f"Error in /finance: {e}", exc_info=True)
        await pd.send("❌ Ошибка при получении финансовой статистики")


@bot.on_command('/test')
async def on_test(pd):
    """Тестовая команда"""
    logger.info("Test command received!")
    await pd.send("✅ Команды работают!")


# Обрабатываем ВСЕ сообщения здесь - и команды, и обычный текст
@bot.on_message()
async def on_any_message(pd):
    """Обработка всех сообщений"""
    try:
        # Получить текст
        body = pd.body
        if hasattr(body, 'text'):
            text = body.text
        else:
            text = str(body)
        
        if not text or not isinstance(text, str):
            return
        
        text = text.strip()
        
        # Обработка команд вручную
        if text.startswith('/'):
            command = text.split()[0].lower()
            
            if command == '/start':
                await on_start(pd)
            elif command == '/test':
                await on_test(pd)
            elif command == '/stats':
                await on_stats(pd)
            elif command == '/website':
                await on_website(pd)
            elif command == '/credentials':
                await on_credentials(pd)
            elif command == '/sleep':
                await on_sleep(pd)
            elif command == '/habits':
                await on_habits(pd)
            elif command == '/finance':
                await on_finance(pd)
            elif command == '/help':
                await on_help(pd)
            else:
                await pd.send("❓ Неизвестная команда. Используй /help")
            return
        
        # Обрабатываем обычный текст через AI
        await handle_ai_message(pd, text)
    
    except Exception as e:
        logger.error(f"Error in on_any_message: {e}", exc_info=True)


if __name__ == "__main__":
    # Явно указываем приоритет обработчиков команд
    # Команды должны обрабатываться ДО общего обработчика сообщений
    logger.info("🚀 AI Бот запущен!")
    logger.info("Зарегистрировано обработчиков команд")
    bot.run()
