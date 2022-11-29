import os
import asyncio
import gspread_asyncio
from google.oauth2.service_account import Credentials
from abc import ABC, abstractmethod
from budget_app.budget_data_description.budget_data_classes import MoneyFlow


class DataCollector(ABC):
    @abstractmethod
    async def save_budget_data(self, budget_data: MoneyFlow) -> None:
        pass


class GoogleSheetsCollector(DataCollector):
    """ Operates with budget data using Google Sheet API """
    def __init__(self, cred_file_name: str = os.path.join(os.path.dirname(__file__), "serviceacct_spreadsheet.json")):
        creds = Credentials.from_service_account_file(cred_file_name)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        self.agcm = gspread_asyncio.AsyncioGspreadClientManager(lambda: scoped)
        self.lock = asyncio.Lock()

    async def save_budget_data(self, budget_data: MoneyFlow) -> None:
        async with self.lock:
            agc = await self.agcm.authorize()

            # Open the spreadsheet and get access to the worksheet
            budget_ss = await agc.open_by_key(os.getenv('GSHEETKEY'))
            worksheet_name: str = budget_data.budget.budget_type.value
            worksheet = await budget_ss.worksheet(worksheet_name)

            # Prepare values for spreadsheet from the MoneyFlow class
            values: list = [
                budget_data.date.strftime('%d.%m.%Y'),
                budget_data.budget.category.value,
                budget_data.value,
                budget_data.comment
            ]

            await worksheet.append_row(values)
