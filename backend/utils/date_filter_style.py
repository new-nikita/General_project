from datetime import date, datetime

ERROR_MESSAGE_INVALID__FORMAT_DATE = "Ошибка, неверный формат даты."
ERROR_MESSAGE_DATE_IS_FUTURE = "Ошибка, дата из будущего времени."

RU_MONTHS = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def custom_date(some_date: datetime | date) -> str:
    """Форматирует дату в читаемый формат с учётом сегодня, вчера и остальных
    дней.

    :param some_date: Дата или datetime для форматирования.
    :return: Строка с форматированной датой.
    """
    today = date.today()
    yesterday = today - date.resolution

    # Приводим к типу date, если это datetime
    if isinstance(some_date, datetime):
        dt = some_date.date()
        time_str = some_date.strftime("%H:%M:%S")
    elif isinstance(some_date, date):
        dt = some_date
        time_str = "00:00:00"
    else:
        raise ValueError(ERROR_MESSAGE_INVALID__FORMAT_DATE)

    if dt > today:
        raise ValueError(ERROR_MESSAGE_DATE_IS_FUTURE)

    if dt == today:
        return f"Сегодня в {time_str}"
    elif dt == yesterday:
        return f"Вчера в {time_str}"
    else:
        day = dt.day
        month = RU_MONTHS.get(dt.month)
        year = dt.year
        return f"{day} {month} {year}"


custom_filters = {"custom_date": custom_date}
