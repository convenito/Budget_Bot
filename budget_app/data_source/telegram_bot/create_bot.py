from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
import os


storage = MemoryStorage()
bot = Bot(token=os.getenv('BOTTOKEN'))
dp = Dispatcher(bot, storage=storage)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
