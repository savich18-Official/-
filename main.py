from aiogram import executor

from create_bot import dp
from bot import on_startup

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)