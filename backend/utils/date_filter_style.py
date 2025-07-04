from datetime import datetime, date, timedelta
import locale

ERROR_MESSAGE_INVALID__FORMAT_DATE = "Ошибка, неверный формат даты."
ERROR_MESSAGE_DATE_IS_FUTURE = "Ошибка, дата из будущего времени."

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


def custom_date(some_date: datetime | date) -> str:
    """
    функция для форматирования даты для вывода
    :param some_date:
    :return:
    """
    today = date.today()
    yesterday = today - timedelta(days=1)

    if isinstance(some_date, datetime):
        dt = some_date.date()
    elif isinstance(some_date, date):
        dt = some_date
    else:
        raise ValueError(ERROR_MESSAGE_INVALID__FORMAT_DATE)

    if dt > today:
        raise ValueError(ERROR_MESSAGE_DATE_IS_FUTURE)

    if dt == today:
        return f"Сегодня в {some_date.strftime('%H:%M:%S')}"
    elif dt == yesterday:
        return f"Вчера в {some_date.strftime('%H:%M:%S')}"
    else:
        day = dt.day
        month_name = dt.strftime("%B")
        year = dt.year
        return f"{day} {month_name} {year}"


custom_filters = {"custom_date": custom_date}
