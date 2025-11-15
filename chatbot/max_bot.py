import aiomax
import logging
from aiomax import fsm
import random

# Создаем бота с токеном и включаем поддержку Markdown
bot = aiomax.Bot("f9LHodD0cOKMptoK2QIqIZPwTC49OHCLNxPYbNK_fo53f2aBZcDMD0C50ypddLazfao7vgAmO3EFZW5cbwBL", default_format="markdown")

# Создаём главное меню с кнопками
main_menu = aiomax.buttons.KeyboardBuilder()
main_menu.add(aiomax.buttons.CallbackButton('🎮 Кликер', 'clicker'))
main_menu.add(aiomax.buttons.CallbackButton('🎲 Случайное число', 'random'))
main_menu.row()
main_menu.add(aiomax.buttons.CallbackButton('📊 Моя статистика', 'stats'))
main_menu.add(aiomax.buttons.CallbackButton('ℹ️ Помощь', 'help'))

# Клавиатура для кликера
clicker_kb = aiomax.buttons.KeyboardBuilder()
clicker_kb.add(aiomax.buttons.CallbackButton('👆 Нажми на меня!', 'click'))
clicker_kb.row()
clicker_kb.add(aiomax.buttons.CallbackButton('🔙 Назад в меню', 'menu'))

# Клавиатура для возврата в меню
back_kb = aiomax.buttons.KeyboardBuilder()
back_kb.add(aiomax.buttons.CallbackButton('🔙 Назад в меню', 'menu'))

# Отправка информации о боте при нажатии кнопки "Начать" в мессенджере
@bot.on_bot_start()
async def info(pd: aiomax.BotStartPayload, cursor: fsm.FSMCursor):
    # Инициализируем данные пользователя
    user_data = cursor.get_data()
    if not user_data:
        user_data = {
            'clicks': 0,
            'random_calls': 0,
            'messages_sent': 0
        }
        cursor.change_data(user_data)
    
    await pd.send(
        "👋 **Привет! Я многофункциональный бот для MAKS!**\n\n"
        "🎯 Что я умею:\n"
        "• 🎮 Кликер - нажимай и набирай очки\n"
        "• 🎲 Генератор случайных чисел\n"
        "• 📊 Статистика твоих действий\n"
        "• 💬 Эхо-режим - повторяю твои сообщения\n\n"
        "Выбери действие:",
        keyboard=main_menu
    )

# Команда /menu - показать главное меню
@bot.on_command('menu')
async def menu_command(ctx: aiomax.CommandContext):
    await ctx.reply("📋 **Главное меню:**\n\nВыбери действие:", keyboard=main_menu)

# Команда /stats - показать статистику
@bot.on_command('stats')
async def stats_command(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
    user_data = cursor.get_data()
    if not user_data:
        user_data = {'clicks': 0, 'random_calls': 0, 'messages_sent': 0}
    
    await ctx.reply(
        f"📊 **Твоя статистика:**\n\n"
        f"👆 Кликов: **{user_data.get('clicks', 0)}**\n"
        f"🎲 Случайных чисел: **{user_data.get('random_calls', 0)}**\n"
        f"💬 Сообщений отправлено: **{user_data.get('messages_sent', 0)}**",
        keyboard=back_kb
    )

# Команда /clicker - запустить кликер
@bot.on_command('clicker')
async def clicker_command(ctx: aiomax.CommandContext, cursor: fsm.FSMCursor):
    user_data = cursor.get_data()
    if not user_data:
        user_data = {'clicks': 0, 'random_calls': 0, 'messages_sent': 0}
    
    clicks = user_data.get('clicks', 0)
    await ctx.reply(
        f"🎮 **Кликер**\n\n"
        f"Твои клики: **{clicks}**\n"
        f"Жми на кнопку!",
        keyboard=clicker_kb
    )

# Команда /help - помощь
@bot.on_command('help')
async def help_command(ctx: aiomax.CommandContext):
    await ctx.reply(
        "ℹ️ **Справка по командам:**\n\n"
        "📋 /menu - главное меню\n"
        "📊 /stats - твоя статистика\n"
        "🎮 /clicker - запустить кликер\n"
        "🎲 /random - случайное число\n"
        "ℹ️ /help - эта справка\n\n"
        "Также можешь просто писать мне сообщения - я буду их повторять!",
        keyboard=back_kb
    )

# Обработка нажатия на кнопку "Кликер"
@bot.on_button_callback('clicker')
async def clicker_button(callback: aiomax.Callback, cursor: fsm.FSMCursor):
    user_data = cursor.get_data()
    if not user_data:
        user_data = {'clicks': 0, 'random_calls': 0, 'messages_sent': 0}
    
    clicks = user_data.get('clicks', 0)
    await callback.answer(
        text=f"🎮 **Кликер**\n\n"
             f"Твои клики: **{clicks}**\n"
             f"Жми на кнопку!",
        keyboard=clicker_kb
    )

# Обработка нажатия на кнопку клика
@bot.on_button_callback('click')
async def on_click(callback: aiomax.Callback, cursor: fsm.FSMCursor):
    user_data = cursor.get_data()
    if not user_data:
        user_data = {'clicks': 0, 'random_calls': 0, 'messages_sent': 0}
    
    user_data['clicks'] = user_data.get('clicks', 0) + 1
    cursor.change_data(user_data)
    
    clicks = user_data['clicks']
    
    # Добавляем мотивирующие сообщения на определенных этапах
    motivation = ""
    if clicks == 10:
        motivation = "\n\n🎉 Отлично! Первые 10 кликов!"
    elif clicks == 50:
        motivation = "\n\n🔥 Wow! 50 кликов!"
    elif clicks == 100:
        motivation = "\n\n⭐ Невероятно! 100 кликов!"
    elif clicks % 100 == 0:
        motivation = f"\n\n💎 Легенда! {clicks} кликов!"
    
    await callback.answer(
        text=f"🎮 **Кликер**\n\n"
             f"Твои клики: **{clicks}**{motivation}",
        keyboard=clicker_kb
    )

# Обработка нажатия на кнопку "Случайное число"
@bot.on_button_callback('random')
async def random_button(callback: aiomax.Callback, cursor: fsm.FSMCursor):
    user_data = cursor.get_data()
    if not user_data:
        user_data = {'clicks': 0, 'random_calls': 0, 'messages_sent': 0}
    
    user_data['random_calls'] = user_data.get('random_calls', 0) + 1
    cursor.change_data(user_data)
    
    number = random.randint(1, 100)
    
    # Добавляем эмодзи в зависимости от числа
    emoji = "🎲"
    if number == 100:
        emoji = "🎰 ДЖЕКПОТ!"
    elif number >= 90:
        emoji = "⭐"
    elif number >= 70:
        emoji = "✨"
    elif number <= 10:
        emoji = "😢"
    
    await callback.answer(
        text=f"🎲 **Случайное число**\n\n"
             f"{emoji} Твоё число: **{number}**\n\n"
             f"Нажми ещё раз для нового числа!",
        keyboard=back_kb
    )

# Обработка нажатия на кнопку "Статистика"
@bot.on_button_callback('stats')
async def stats_button(callback: aiomax.Callback, cursor: fsm.FSMCursor):
    user_data = cursor.get_data()
    if not user_data:
        user_data = {'clicks': 0, 'random_calls': 0, 'messages_sent': 0}
    
    await callback.answer(
        text=f"📊 **Твоя статистика:**\n\n"
             f"👆 Кликов: **{user_data.get('clicks', 0)}**\n"
             f"🎲 Случайных чисел: **{user_data.get('random_calls', 0)}**\n"
             f"💬 Сообщений отправлено: **{user_data.get('messages_sent', 0)}**",
        keyboard=back_kb
    )

# Обработка нажатия на кнопку "Помощь"
@bot.on_button_callback('help')
async def help_button(callback: aiomax.Callback):
    await callback.answer(
        text="ℹ️ **Справка по командам:**\n\n"
             "📋 /menu - главное меню\n"
             "📊 /stats - твоя статистика\n"
             "🎮 /clicker - запустить кликер\n"
             "🎲 /random - случайное число\n"
             "ℹ️ /help - эта справка\n\n"
             "Также можешь просто писать мне сообщения - я буду их повторять!",
        keyboard=back_kb
    )

# Обработка нажатия на кнопку "Назад в меню"
@bot.on_button_callback('menu')
async def menu_button(callback: aiomax.Callback):
    await callback.answer(
        text="📋 **Главное меню:**\n\nВыбери действие:",
        keyboard=main_menu
    )

# Функция будет выполняться при отправке любого сообщения (эхо-режим)
@bot.on_message()
async def echo(message: aiomax.Message, cursor: fsm.FSMCursor):
    user_data = cursor.get_data()
    if not user_data:
        user_data = {'clicks': 0, 'random_calls': 0, 'messages_sent': 0}
    
    user_data['messages_sent'] = user_data.get('messages_sent', 0) + 1
    cursor.change_data(user_data)
    
    # Разные варианты ответов для разнообразия
    responses = [
        f"💬 Вы написали: {message.content}",
        f"📝 Повторяю: {message.content}",
        f"🔄 Эхо: {message.content}",
        f"✍️ Получил сообщение: {message.content}"
    ]
    
    await message.reply(random.choice(responses))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot.run()
