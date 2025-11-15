"""
Главный файл бота - точка входа (AI версия)
"""
import aiomax
import logging

from config import bot_config
from handlers.ai_aiomax import register_ai_handlers


def create_bot() -> aiomax.Bot:
    """
    Создание и настройка экземпляра бота
    
    Returns:
        Настроенный экземпляр бота
    """
    bot = aiomax.Bot(
        bot_config.token,
        default_format=bot_config.default_format
    )
    
    # Регистрируем только AI обработчики
    register_ai_handlers(bot)
    
    return bot


def main():
    """Запуск бота"""
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, bot_config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Создаем и запускаем бота
    bot = create_bot()
    
    logging.info("🚀 Бот запущен!")
    bot.run()


if __name__ == "__main__":
    main()
