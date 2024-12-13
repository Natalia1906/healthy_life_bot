import asyncio
import logging
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import argparse
from config import TOKEN
from handlers import router
from database import Database


# https://docs.python.org/3/library/signal.html
# https://sky.pro/media/rabota-s-signalom-sigint-v-python/
def signal_handler(signum, frame):
    """Обработчик сигналов завершения работы.

    Корректно завершает работу бота при получении сигналов
    SIGINT (Ctrl+C) или SIGKILL (kill).

    Args:
        signum: номер сигнала, который был отправлен процессу
        frame: текущий stack frame в момент получения сигнала

    Returns:
        None
    """

    print('\nExit')
    sys.exit(0)


async def main():
    """Главная функция запуска бота.

    Выполняет следующие действия:
    - Настраивает обработку сигналов завершения
    - Инициализирует базу данных
    - Настраивает логгирование
    - Создает и запускает бота с поддержкой FSM

    Args:
        None

    Returns:
        None
    """

    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill

    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='Fitness Bot')
    parser.add_argument('--reset-db', action='store_true')
    args = parser.parse_args()  # добавляем флаг для сброса БД

    logging.basicConfig(level=logging.INFO)

    if args.reset_db:
        import os
        if os.path.exists('fitness.db'):
            os.remove('fitness.db')
    db = Database()
    db.create_tables()

    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(router)

    # https://ru.stackoverflow.com/questions/1460449/Как-сделать-чтобы-определенный-код-функция-срабатывал-при-запуске-закрытии-бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # Пропускаем накопившиеся апдейты и запускаем polling


if __name__ == '__main__':
    asyncio.run(main())
