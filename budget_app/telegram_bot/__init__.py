from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ..data_collector import DataCollector

from .handlers import router


class TelegramSource:
    def __init__(
            self,
            bot_token: str,
            data_collectors: list[DataCollector],
    ) -> None:
        self.bot = Bot(bot_token)
        self.data_collectors = data_collectors
        self.dispatcher: Dispatcher = self.get_dispatcher()

    def get_dispatcher(self) -> Dispatcher:
        dispatcher = Dispatcher(
            storage=MemoryStorage(),
            data_collectors=self.data_collectors
        )
        dispatcher.include_router(router)
        return dispatcher

    async def start(self) -> None:
        await self.dispatcher.start_polling(self.bot)

    async def stop(self) -> None:
        await self.dispatcher.stop_polling()
