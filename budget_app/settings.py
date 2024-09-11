from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    token: str
    gsheetkey: str
