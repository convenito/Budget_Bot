from enum import StrEnum
from typing import Type
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_keyboard(budget_class: Type[StrEnum]) -> InlineKeyboardMarkup:
    """ Function creates keyboard to choose category from the budget_class StrEnum """
    budget_class_options = list(budget_class)
    # Text on buttons is big, so only 2 buttons per row
    buttons = [
        [
            InlineKeyboardButton(text=k, callback_data=k)
            for k in budget_class_options[i: i+2]
        ] for i in range(0, len(budget_class_options), 2)
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
