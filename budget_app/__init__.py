import logging

from .telegram_bot import TelegramSource
from .data_collector import GoogleSheetsCollector
from .settings import BotSettings


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    bot_settings = BotSettings()
    logging.info("Starting the Data Collectors...")
    data_collectors = [
        GoogleSheetsCollector(
            bot_settings.gsheetkey, bot_settings.google_service_json_file
        )
    ]
    logging.info("Data Collectors started successfully")
    tg_bot = TelegramSource(bot_settings.token, data_collectors)
    logging.info("Start the telegram bot")
    await tg_bot.start()
