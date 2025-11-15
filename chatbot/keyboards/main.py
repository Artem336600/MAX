"""
Клавиатуры бота
"""
import aiomax


def get_main_menu() -> aiomax.buttons.KeyboardBuilder:
    """Главное меню с кнопками"""
    kb = aiomax.buttons.KeyboardBuilder()
    kb.add(aiomax.buttons.CallbackButton('🎮 Кликер', 'clicker'))
    kb.add(aiomax.buttons.CallbackButton('🎲 Случайное число', 'random'))
    kb.row()
    kb.add(aiomax.buttons.CallbackButton('📊 Моя статистика', 'stats'))
    kb.add(aiomax.buttons.CallbackButton('ℹ️ Помощь', 'help'))
    return kb


def get_clicker_keyboard() -> aiomax.buttons.KeyboardBuilder:
    """Клавиатура для кликера"""
    kb = aiomax.buttons.KeyboardBuilder()
    kb.add(aiomax.buttons.CallbackButton('👆 Нажми на меня!', 'click'))
    kb.row()
    kb.add(aiomax.buttons.CallbackButton('🔙 Назад в меню', 'menu'))
    return kb


def get_back_keyboard() -> aiomax.buttons.KeyboardBuilder:
    """Клавиатура с кнопкой возврата в меню"""
    kb = aiomax.buttons.KeyboardBuilder()
    kb.add(aiomax.buttons.CallbackButton('🔙 Назад в меню', 'menu'))
    return kb


def get_custom_keyboard(buttons: list[tuple[str, str]], rows: list[int] = None) -> aiomax.buttons.KeyboardBuilder:
    """
    Создание кастомной клавиатуры
    
    Args:
        buttons: Список кортежей (текст, callback_data)
        rows: Список с количеством кнопок в каждом ряду
        
    Returns:
        KeyboardBuilder с настроенными кнопками
    """
    kb = aiomax.buttons.KeyboardBuilder()
    
    if rows is None:
        # Все кнопки в один ряд
        for text, callback_data in buttons:
            kb.add(aiomax.buttons.CallbackButton(text, callback_data))
    else:
        # Распределяем кнопки по рядам
        button_index = 0
        for row_size in rows:
            for _ in range(row_size):
                if button_index < len(buttons):
                    text, callback_data = buttons[button_index]
                    kb.add(aiomax.buttons.CallbackButton(text, callback_data))
                    button_index += 1
            kb.row()
    
    return kb
