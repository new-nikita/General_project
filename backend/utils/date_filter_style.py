from datetime import datetime, date, timedelta

def custom_date(some_date: datetime) -> str:
    today = date.today()
    yesterday = today - timedelta(days=1)

    if isinstance(some_date, datetime):
        dt = some_date.date()
    else:
        dt = some_date

    if dt == today:
        return f"Сегодня в {some_date.strftime('%H:%M:%S')}"
    elif dt == yesterday:
        return f"Вчера в {some_date.strftime('%H:%M:%S')}"
    else:
        return dt.strftime("%d %B %Y")

custom_filters = {'custom_date': custom_date}