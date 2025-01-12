import logging

from aiogram import executor, Bot
from aiogram.types.bot_command import BotCommand

import db
from create_bot import dp, bot
from handlers import registr_handlers


# Исправленный вызов logging.basicConfig без аргумента encoding
logging.basicConfig(level=logging.INFO,
                    # filename='bot.log',
                    filemode='a',
                    format="%(asctime)s %(levelname)s %(message)s"
                    )
logging.getLogger(__name__)

async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="/low", description="Категории поиска в порядке возрастания"),
        BotCommand(command="/hight", description="Категории поиска в порядке убывания"),
        BotCommand(command="/custom", description="Категории в выбранном интервале рейтинга"),
        BotCommand(command="/history", description="История запросов"),
        BotCommand(command="/cancel", description="Отмена выбранного действия")
    ]
    await bot.set_my_commands(commands)

async def on_startup(_):
    logging.info('Бот вышел в сеть')
    db.sql_start()
    await set_commands(bot)

registr_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
