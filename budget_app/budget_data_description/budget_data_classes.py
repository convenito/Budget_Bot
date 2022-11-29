from pydantic import BaseModel, Field
from typing import Optional, Literal, Type, Dict
import datetime
from aenum import StrEnum


class BudgetType(StrEnum):
    """ Types of budget data """
    INCOME = 'Приход'
    DAILYSPENT = 'Повседневные'
    FLATSPENT = 'Квартира'
    VACATIONSPENT = 'Отпуск'


class CategoryIncome(StrEnum):
    """ Class contains income budget categories """
    SALARY = 'Заработная плата'
    CASHBACK = 'Кэшбэк'
    BONUS = 'Премия'
    TAXRETURN = 'Налоговый вычет'
    DIVIDENDS = 'Дивиденды'
    OTHERS = 'Прочее'


class CategoryDailySpent(StrEnum):
    """ Class contains daily spent categories """
    FOOD = 'Питание'
    TRANSPORT = 'Проезд'
    CLOTHES = 'Одежда'
    PRESENTS = 'Подарки'
    HEALTH = 'Здоровье'
    ENTERTAINMENT = 'Развлечения'
    FITNESS = 'Фитнес'
    SMALL_PURCHASES = 'Мелкие покупки'
    CHEMICALS = 'Бытовая химия'


class CategoryFlatSpent(StrEnum):
    """ Class contains categories of spents for flat """
    RENT = 'Аренда'
    UTILITIES = 'ЖКХ, Интернет'
    MORTGAGE = 'Ипотека'
    FURNITURE = 'Мебель'
    DECOR = 'Декор'
    DEVICES = 'Техника, приборы'
    OTHERS = 'Прочее'


class CategoryVacationSpent(StrEnum):
    """ Class contains categories for spents on vacation """
    TICKETS = 'Билеты'
    LIVING = 'Проживание'
    MONEY = 'Деньги с собой'
    EAT = 'Питание'


class BudgetIncome(BaseModel):
    """ Class for income budget data """
    budget_type: Literal[BudgetType.INCOME]  # type: ignore
    category: CategoryIncome


class BudgetDailySpent(BaseModel):
    """ Class for daily spent budget data """
    budget_type: Literal[BudgetType.DAILYSPENT]  # type: ignore
    category: CategoryDailySpent


class BudgetFlatSpent(BaseModel):
    """ Class for flat spents budget data """
    budget_type: Literal[BudgetType.FLATSPENT]  # type: ignore
    category: CategoryFlatSpent


class BudgetVacationSpent(BaseModel):
    """ Class for vacation spents budget data """
    budget_type: Literal[BudgetType.VACATIONSPENT]  # type: ignore
    category: CategoryVacationSpent


class MoneyFlow(BaseModel):
    """ BaseModel for budget data """
    budget: BudgetIncome | BudgetDailySpent | BudgetFlatSpent | BudgetVacationSpent = Field(..., discriminator='budget_type')
    date: datetime.datetime | datetime.date
    value: int
    comment: Optional[str]


# Category map for telegram bot keyboard to choose right categories from budget type
category_map: Dict[BudgetType, Type[StrEnum]] = {
    BudgetType.INCOME: CategoryIncome,
    BudgetType.DAILYSPENT: CategoryDailySpent,
    BudgetType.FLATSPENT: CategoryFlatSpent,
    BudgetType.VACATIONSPENT: CategoryVacationSpent,
}


def convert_to_money_flow(data: dict) -> MoneyFlow:
    """ Function to convert raw data from telegram bot into MoneyFLow class object """
    required_keys = ['budget_type', 'category']
    final_data = {
        'budget': {k: v for k, v in data.items() if k in required_keys},
        'date': data.get('date'),
        'value': data.get('value'),
        'comment': data.get('comment')
    }
    return MoneyFlow(**final_data)
