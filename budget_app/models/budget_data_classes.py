import datetime
from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Literal, Type, Dict


class Currency(StrEnum):
    EUR = "EUR"
    RUB = "RUB"


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
    CAFE = 'Кафе, рестораны'
    ALCO = 'Алкоголь'
    TRANSPORT = 'Проезд'
    CLOTHES = 'Одежда'
    PRESENTS = 'Подарки'
    HEALTH = 'Здоровье'
    ENTERTAINMENT = 'Развлечения'
    FITNESS = 'Фитнес'
    SMALL_PURCHASES = 'Мелкие покупки'
    CHEMICALS = 'Бытовая химия'
    EDUCATION = 'Обучение, английский'
    TAXES = 'Налоги'
    BEAUTY = 'Уход, косметика'


class CategoryFlatSpent(StrEnum):
    """ Class contains categories of spent for flat """
    RENT = 'Аренда'
    UTILITIES = 'ЖКХ, Интернет'
    MORTGAGE = 'Ипотека'
    FURNITURE = 'Мебель'
    DECOR = 'Декор'
    DEVICES = 'Техника, приборы'
    OTHERS = 'Прочее'


class CategoryVacationSpent(StrEnum):
    """ Class contains categories for spent on vacation """
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
    """ Class for flat spent budget data """
    budget_type: Literal[BudgetType.FLATSPENT]  # type: ignore
    category: CategoryFlatSpent


class BudgetVacationSpent(BaseModel):
    """ Class for vacation spent budget data """
    budget_type: Literal[BudgetType.VACATIONSPENT]  # type: ignore
    category: CategoryVacationSpent


class MoneyFlow(BaseModel):
    """ BaseModel for budget data """
    budget: BudgetIncome | BudgetDailySpent | BudgetFlatSpent | BudgetVacationSpent = Field(
        ..., discriminator='budget_type')
    date: datetime.datetime | datetime.date
    value: float
    currency: Currency = Currency.EUR
    comment: str | None = None


# Category map for telegram bot keyboard to choose right categories from budget type
category_map: Dict[BudgetType, Type[StrEnum]] = {
    BudgetType.INCOME: CategoryIncome,
    BudgetType.DAILYSPENT: CategoryDailySpent,
    BudgetType.FLATSPENT: CategoryFlatSpent,
    BudgetType.VACATIONSPENT: CategoryVacationSpent,
}
