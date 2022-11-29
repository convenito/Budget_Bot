from aiogram import executor
from .data_source.telegram_bot.create_bot import dp, shutdown
from .data_source.telegram_bot.handlers import register_all_handlers


def main():
    register_all_handlers(dp)
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
