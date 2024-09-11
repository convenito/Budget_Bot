from datetime import datetime, timedelta, date

from ..models import MoneyFlow, Currency


def process_date(date_message: str) -> datetime | None:
    if date_message.lower() == "today":
        budget_date = datetime.today()
    elif date_message.lower() == "yesterday":
        budget_date = datetime.today() - timedelta(days=1)
    else:
        try:
            budget_date: datetime = datetime.strptime(
                date_message, '%d.%m'
            ).replace(year=date.today().year)
        except ValueError:
            return None
    return budget_date


def convert_to_money_flow(data: dict) -> MoneyFlow:
    """ Function to convert raw data from telegram bot into MoneyFLow class object """
    required_keys = ['budget_type', 'category']
    return MoneyFlow.model_validate({
        'budget': {k: v for k, v in data.items() if k in required_keys},
        'date': data.get('date'),
        'value': data.get('value'),
        'currency': Currency(data.get('currency')),
        'comment': data.get('comment')
    })
