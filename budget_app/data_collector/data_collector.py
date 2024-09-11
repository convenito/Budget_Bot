import os
import asyncio
import gspread_asyncio
import logging
from abc import ABC, abstractmethod

from google.oauth2.service_account import Credentials

from ..models import MoneyFlow


class DataCollector(ABC):
    @abstractmethod
    async def save_budget_data(self, budget_data: MoneyFlow) -> None:
        pass


class GoogleSheetsCollector(DataCollector):
    """ Operates with budget data using Google Sheet API """

    def __init__(self, sheet_key: str) -> None:
        self.sheet_key = sheet_key
        self.scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        self.agcm = gspread_asyncio.AsyncioGspreadClientManager(self.get_creds)
        self.write_lock = asyncio.Lock()

    def get_creds(self):
        file_name = os.path.join(
            os.path.dirname(__file__), "serviceacct_spreadsheet.json"
        )
        creds = Credentials.from_service_account_file(file_name)
        return creds.with_scopes(self.scopes)

    async def save_budget_data(self, budget_data: MoneyFlow) -> None:
        async with self.write_lock:
            logging.info(f"Saving budget data: {budget_data}")
            agc = await self.agcm.authorize()
            # Open the spreadsheet and get access to the worksheet
            budget_ss = await agc.open_by_key(self.sheet_key)
            worksheet_name: str = budget_data.budget.budget_type.value
            worksheet = await budget_ss.worksheet(worksheet_name)

            # Prepare values for spreadsheet from the MoneyFlow class
            values: list = [
                budget_data.date.strftime('%d.%m.%Y'),
                budget_data.budget.category.value,
                budget_data.value,
                budget_data.currency,
                budget_data.comment,
            ]

            await worksheet.append_row(values)
