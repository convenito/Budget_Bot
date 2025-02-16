import asyncio
from datetime import datetime
import logging
from typing import Any

from aiogram import types as t, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from .bot_keyboards import get_keyboard
from .actions import process_date, convert_to_money_flow
from ..models.budget_data_classes import BudgetType, MoneyFlow, category_map
from ..data_collector import DataCollector

router = Router()


# Create states for FSM
class FSMStates(StatesGroup):
    budget_type = State()
    category = State()
    date = State()
    value = State()
    currency = State()
    comment = State()


@router.message(Command("help"))
async def send_welcome(message: t.Message) -> None:
    """Welcome message and description how to use bot"""
    await message.answer(
        "This bot is for personal financial accounting\n\n"
        "You can add expenses or income with command: `/add`\n"
        "Bot will ask you for budget type, category, date, value, currency and comment\n"
        "For date please use `DD.MM` format (year is current year).\n"
        "For 'today' you can just type 'today'. For yesterday type 'yesterday'\n"
        "Comments are optional - you can add them or not.\n\n"
        "You can cancel input anytime just enter 'cancel'",
        reply_markup=ReplyKeyboardRemove(),
    )


# Start conversation with the bot and get the budget type using InlineKeyboard
@router.message(Command(commands=["add", "start"]))
async def command_start(message: t.Message, state: FSMContext) -> Any:
    """ Send message with keyboard to choose budget type """
    await state.set_state(FSMStates.budget_type)
    reply = await message.reply(
        '1. Choose type:', reply_markup=get_keyboard(BudgetType)
    )
    await state.update_data(reply_message_id=reply.message_id)
    current_state = await state.get_state()
    logging.info(f"Got message: {message.text}. Entering FSM. "
                 f"Current state: {current_state}")


# Handle all states for cancel
@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: t.Message, state: FSMContext):
    # Cancel state and inform user about it
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.reply(
        'Procedure was canceled. If you want to add new data - please use "/add" command',
        reply_markup=ReplyKeyboardRemove(),
    )


# Handle the callback from budget_type keyboard and store budget_type data in memory
@router.callback_query(FSMStates.budget_type)
async def process_budget_type(callback: t.CallbackQuery, state: FSMContext) -> None:
    """ Send message with keyboard to choose category of chosen budget type"""
    budget_type = BudgetType(callback.data)
    await callback.answer(text=f"1/6 - Budget type: {budget_type.value}")
    logging.info(f"Got budget type: {budget_type.value}. "
                 f"Current state: {await state.get_state()}")

    # Remove inline keyboard from previous message and edit message
    state_data = await state.get_data()
    reply_message_id = state_data.get('reply_message_id')
    if reply_message_id:
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=reply_message_id,
            text=f"1/6 - Budget type: {budget_type.value}",
            reply_markup=None
        )

    await state.update_data(budget_type=callback.data)
    await state.set_state(FSMStates.category)

    reply = await callback.message.answer(
        f'2. Choose category:',
        reply_markup=get_keyboard(category_map.get(budget_type))
    )
    await state.update_data(reply_message_id=reply.message_id)


# Handle the callback from category keyboard and store category in memory
@router.callback_query(FSMStates.category)
async def process_category(callback: t.CallbackQuery, state: FSMContext) -> None:
    """ Request date from user message """
    chosen_category = callback.data
    await callback.answer(text=f'2/6 - Category: {chosen_category.capitalize()}')
    logging.info(f"Got category: {chosen_category}. "
                 f"Current state: {await state.get_state()}")

    # Remove inline keyboard from previous message and edit text
    state_data = await state.get_data()
    reply_message_id = state_data.get('reply_message_id')
    if reply_message_id:
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=reply_message_id,
            text=f'2/6 - Category: {chosen_category.capitalize()}',
            reply_markup=None
        )

    await state.update_data(category=chosen_category)
    await state.set_state(FSMStates.date)

    reply = await callback.message.answer(
        f'3. Please enter date - "today", "yesterday" or in format DD.MM',
        reply_markup=t.InlineKeyboardMarkup(inline_keyboard=[
            [
                t.InlineKeyboardButton(text="today", callback_data="today"),
                t.InlineKeyboardButton(text="yesterday", callback_data="yesterday")
            ]
        ]))
    await state.update_data(reply_message_id=reply.message_id)


@router.message(FSMStates.date)
async def process_any_date(message: t.Message, state: FSMContext) -> None:
    budget_date = process_date(message.text)
    if budget_date is None:
        await message.reply(
            'Wrong date format. Please enter DD.MM (example: 31.11) '
            'or "/cancel" to exit'
        )
        return

    # Remove inline keyboard from previous message and edit text
    state_data = await state.get_data()
    reply_message_id = state_data.get('reply_message_id')
    if reply_message_id:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=reply_message_id,
            text=f'3/6 - Date: {datetime.strftime(budget_date, "%d/%m/%Y")}',
            reply_markup=None,
        )

    await state.update_data(date=budget_date)
    await state.set_state(FSMStates.value)
    reply = await message.answer("4. Please enter sum:")
    await state.update_data(reply_message_id=reply.message_id)


@router.callback_query(FSMStates.date)
async def process_date_from_keyboard(
        callback: t.CallbackQuery,
        state: FSMContext
) -> None:
    budget_date = process_date(callback.data)
    if budget_date is None:
        await callback.message.reply(
            'Wrong date format. Please enter DD.MM (example: 31.11) '
            'or "/cancel" to exit'
        )
        return
    current_date = datetime.strftime(budget_date, "%d/%m/%Y")
    current_state = await state.get_state()
    await callback.answer(text=f'3/6 - Date: {current_date}')
    logging.info(f"Got date: {current_date}. Current state: {current_state}")

    # Remove inline keyboard from previous message and edit text
    state_data = await state.get_data()
    reply_message_id = state_data.get('reply_message_id')
    if reply_message_id:
        await callback.message.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=reply_message_id,
            text=f'3/6 - Date: {datetime.strftime(budget_date, "%d/%m/%Y")}',
            reply_markup=None,
        )

    await state.update_data(date=budget_date)
    await state.set_state(FSMStates.value)
    reply = await callback.message.answer("4. Please enter sum:")
    await state.update_data(reply_message_id=reply.message_id)


@router.message(FSMStates.value)
async def process_value(message: t.Message, state: FSMContext) -> None:
    try:
        value = round(float(message.text), 1)
    except ValueError:
        await message.reply(
            'Please enter only numbers without literals '
            'or enter "/cancel" to exit'
        )
        return

    # Remove inline keyboard from previous message and edit text
    state_data = await state.get_data()
    reply_message_id = state_data.get('reply_message_id')
    if reply_message_id:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=reply_message_id,
            text=f'4/6 - Sum: {value}',
            reply_markup=None,
        )

    await state.update_data(value=value)
    await state.set_state(FSMStates.currency)
    reply = await message.reply(
        '5. Choose currency: EUR or RUB:',
        reply_markup=t.InlineKeyboardMarkup(
            inline_keyboard=[
                [t.InlineKeyboardButton(text="EUR", callback_data="EUR"),
                 t.InlineKeyboardButton(text="RUB", callback_data="RUB")]
            ]
        )
    )
    await state.update_data(reply_message_id=reply.message_id)


@router.callback_query(FSMStates.currency)
async def process_currency(callback: t.CallbackQuery, state: FSMContext) -> None:
    currency = callback.data
    await callback.answer(text=f'5/6 - Currency: {currency}')

    # Remove inline keyboard from previous message and edit text
    state_data = await state.get_data()
    reply_message_id = state_data.get('reply_message_id')
    if reply_message_id:
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=reply_message_id,
            text=f'5/6 - Currency: {currency}',
            reply_markup=None,
        )

    await state.update_data(currency=currency)
    await state.set_state(FSMStates.comment)
    reply = await callback.message.answer(
        '6. Enter comment or press "finish"',
        reply_markup=t.ReplyKeyboardMarkup(keyboard=[[t.KeyboardButton(text='finish')]])
    )
    await state.update_data(reply_message_id=reply.message_id)


# Handle comment for the current budget data
@router.message(FSMStates.comment)
async def get_comment(
        message: t.Message,
        state: FSMContext,
        data_collectors: list[DataCollector],
) -> None:
    comment = message.text if message.text != 'finish' else None
    await message.reply(
        f"6. Comment: {comment if comment is not None else 'no comment'}",
        reply_markup=ReplyKeyboardRemove(),
    )
    data = await state.get_data()
    data['comment'] = comment
    model_data: MoneyFlow = convert_to_money_flow(data)
    await asyncio.gather(*[
        collector.save_budget_data(model_data)
        for collector in data_collectors
    ])
    await message.bot.send_message(
        chat_id=message.chat.id,
        text="Budget data successfully saved!",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()
