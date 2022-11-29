from abc import ABC, abstractmethod
from budget_app.data_collector.data_collector import DataCollector
from .telegram_bot.create_bot import bot, dp


class DataSource(ABC):
    @abstractmethod
    def listen_and_send_to_collector(self):
        pass


class TelegramSource(DataSource):
    def __init__(self, bot=bot, dp=dp):
        self.bot = bot
        self.dp = dp


    def listen_and_send_to_collector(self, data_collector: DataCollector):
        pass
