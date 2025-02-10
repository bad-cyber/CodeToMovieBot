import logging
import asyncio
from aiogram.filters import Command
from dispatcher import dp
from bot import bot
from config.config import LOG_LEVEL, LOG_FORMAT

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)

async def main():
    # Запуск бота
    logging.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
