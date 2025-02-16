import os
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    token: str
    gsheetkey: str
    google_service_json_file: str = os.path.join(
        os.path.dirname(__file__), "serviceacct_spreadsheet.json")
