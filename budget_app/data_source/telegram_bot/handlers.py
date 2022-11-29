import datetime
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from .create_bot import bot
from .bot_keyboards import get_keyboard
from budget_app.budget_data_description.budget_data_classes import (
    BudgetType, CategoryIncome, CategoryFlatSpent, CategoryDailySpent, CategoryVacationSpent, MoneyFlow,
    category_map, convert_to_money_flow
)
from aiogram.dispatcher.filters.state import State, StatesGroup
from budget_app.data_collector.data_collector import GoogleSheetsCollector


# Create states for FSM
class FSMStates(StatesGroup):
    budget_type = State()
    category = State()
    date = State()
    value = State()
    comment = State()


async def send_welcome(message: Message):
    """Welcome message and description how to use bot"""
    await message.answer(
        "This bot is for personal financial accounting\n\n"
        "You can add expenses or income with command: /add\n"
        "Bot will ask you for budget type, category, date, value and comment\n"
        "For date please use DD.MM format (Year always 2022 for now).\n"
        "For 'today' you can just send empty message or type 'today'. For yesterday type 'yesterday'\n"
        "Comments are optional - you can add them or not.\n\n"
        "You can cancel input anytime just enter 'cancel'"
    )


# Start conversation with the bot and get the budget type using InlineKeyboard
async def send_budget_types(message: Message):
    """ Send message with keyboard to choose budget type """
    markup = get_keyboard(BudgetType)
    await FSMStates.budget_type.set()
    await message.reply(text='Hi! Choose type:', reply_markup=markup)


# Handle the callback from budget_type keyboard and store budget_type data in memory
async def get_budget_type(callback: CallbackQuery, state: FSMContext):
    """ Send message with keyboard to choose category of chosen budget type"""
    await bot.answer_callback_query(callback.id)
    budget_type = BudgetType(callback.data)
    category = category_map.get(budget_type)
    async with state.proxy() as data:
        data['budget_type'] = callback.data
    markup = get_keyboard(category)
    await FSMStates.next()
    await bot.send_message(
        callback.message.chat.id,
        text=f'Chosen: "{callback.data}". Now choose category:',
        reply_markup=markup)


# Handle the callback from category keyboard and store category in memory
async def category_button(callback: CallbackQuery, state: FSMContext):
    """ Request date from user message """
    await bot.answer_callback_query(callback.id)
    async with state.proxy() as data:
        data['category'] = callback.data
    await FSMStates.next()
    await bot.send_message(
        callback.message.chat.id,
        text=f'Category: "{callback.data}". Please enter date in format DD.MM (or simply "today" or "yesterday"):',
    )


# Handle the date ond store it in memory
async def get_date(message: Message, state: FSMContext):
    if message.text.lower() == 'today' or message.text.lower() == '' or message.text.lower() == 'сегодня':
        async with state.proxy() as data:
            data['date'] = datetime.date.today()
    elif message.text.lower() == 'yesterday' or message.text.lower() == 'вчера':
        async with state.proxy() as data:
            data['date'] = (datetime.date.today()-datetime.timedelta(days=1))
    else:
        try:
            correct_date: datetime = datetime.datetime.strptime(message.text, '%d.%m').replace(year=datetime.date.today().year)
            async with state.proxy() as data:
                data['date'] = correct_date
        except ValueError:
            await message.reply('Wrong date format. Please enter DD.MM (example: 04.11) or "/cancel" to exit')
    await FSMStates.next()
    await bot.send_message(message.chat.id, text="How much was the fish? Please enter value:")


# @dp.message_handler(state=FSMStates.value)
async def get_value(message: Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['value'] = int(message.text)
    except ValueError:
        await message.reply('Please enter only numbers without literals or enter "/cancel" to exit')
    await FSMStates.next()
    await bot.send_message(message.chat.id, 'Okay, the last, but not the least. Enter comment:')


# Handle comment for the current budget data
async def get_comment(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
        correct_full_data: MoneyFlow = convert_to_money_flow(data)
    google_collector = GoogleSheetsCollector()
    await google_collector.save_budget_data(correct_full_data)
    await state.finish()


# Handle all states for cancel
async def cancel_handler(message: Message, state: FSMContext):
    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Procedure was canceled. If you want to add new data - please use "/add" command')


def register_all_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    dp.register_message_handler(send_budget_types, commands=['Add'], state=None)
    dp.register_callback_query_handler(get_budget_type, text=list(BudgetType), state=FSMStates.budget_type)
    dp.register_callback_query_handler(
        category_button,
        text=list(CategoryIncome)+list(CategoryDailySpent)+list(CategoryFlatSpent)+list(CategoryVacationSpent),
        state=FSMStates.category
    )
    dp.register_message_handler(get_date, state=FSMStates.date)
    dp.register_message_handler(get_value, state=FSMStates.value)
    dp.register_message_handler(get_comment, state=FSMStates.comment)
    dp.register_message_handler(cancel_handler, state='*', commands=['cancel'])
    dp.register_message_handler(cancel_handler, lambda message: message.text.lower() == 'cancel', state='*')

