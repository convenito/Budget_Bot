from aenum import StrEnum
from typing import Type
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_keyboard(budget_class: Type[StrEnum]) -> InlineKeyboardMarkup:
    """ Function creates keyboard to choose category from the StrEnum classes of budget data classes """
    bc_keyboard = InlineKeyboardMarkup()
    for i in list(budget_class):
        button = InlineKeyboardButton(i, callback_data=i)
        bc_keyboard.add(button)
    return bc_keyboard
