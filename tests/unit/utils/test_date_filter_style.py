import random
from datetime import date, datetime, timedelta

import pytest

from backend.utils.date_filter_style import (
    ERROR_MESSAGE_DATE_IS_FUTURE,
    ERROR_MESSAGE_INVALID__FORMAT_DATE,
    RU_MONTHS,
    custom_date,
)


@pytest.mark.parametrize(
    "input_date, expected_output",
    [
        (datetime.now(), f"Сегодня в {datetime.now().strftime('%H:%M:%S')}"),
        (
            today := datetime.now() - timedelta(hours=1),
            f"Сегодня в {today.strftime('%H:%M:%S')}",
        ),
        (
            yesterday := datetime.now() - timedelta(days=1),
            f"Вчера в {yesterday.strftime('%H:%M:%S')}",
        ),
        (
            any_other_day := datetime.now() - timedelta(days=random.randint(2, 30)),
            f"{any_other_day.day} {RU_MONTHS[any_other_day.month]} {any_other_day.year}",
        ),
    ],
)
def test_valid_date_custom_date(
    input_date: datetime,
    expected_output: str,
) -> None:
    """Тестирует валидные даты."""
    assert custom_date(input_date) == expected_output


def test_random_past_days_custom_date() -> None:
    """Тестирует случайные прошлые дни."""
    for _ in range(5):
        past_days = random.randint(2, 365 * 10)
        past_date = datetime.now() - timedelta(days=past_days)
        result = custom_date(past_date)
        assert result.endswith(f"{past_date.year}")


def test_start_of_month_custom_date() -> None:
    """Проверяет первую дату текущего месяца."""
    first_day_of_month = datetime(datetime.now().year, datetime.now().month, 1)
    result = custom_date(first_day_of_month)
    assert result != "Сегодня", "Первая дата месяца должна отличаться от 'Сегодня'"


def test_end_of_last_month_custom_date() -> None:
    """Проверяет последнюю дату предыдущего месяца."""
    last_day_prev_month = datetime.now().replace(day=1) - timedelta(days=1)
    result = custom_date(last_day_prev_month)
    assert not result.startswith(
        "Сегодня"
    ), "Последняя дата прошлого месяца не должна начинаться с 'Сегодня'"


def test_date_input_type() -> None:
    """Проверяет обработку типа 'date'."""
    today_as_date = date.today()
    result = custom_date(today_as_date)
    assert result.startswith("Сегодня"), "Результат для даты должен содержать 'Сегодня'"


def test_string_input() -> None:
    """Проверяет строку формата 'YYYY-MM-DD'."""
    current_year = datetime.now().year
    string_date = f"{current_year}-01-01"
    parsed_date = datetime.strptime(string_date, "%Y-%m-%d").date()
    result = custom_date(parsed_date)
    assert (
        result == f"1 января {current_year}"
    ), "Ошибка обработки строкового формата даты"


@pytest.mark.parametrize(
    "invalid_date, expected_error",
    [
        ("2023-02-30", "day is out of range for month"),
        ("2023-13-01", "month must be in 1..12"),
        ("2023-01-55", "day is out of range for month"),
        ("2023-01-00", "day is out of range for month"),
        ("-2023-01-01", "Invalid isoformat string"),
    ],
)
def test_invalid_format_date(invalid_date: str, expected_error: str) -> None:
    """Проверяет невалидные даты в месяцах и днях."""
    with pytest.raises(ValueError) as exc_info:
        date_formatted = date.fromisoformat(invalid_date)
        custom_date(date_formatted)

    assert expected_error in str(exc_info.value), "Ошибка обработки невалидной даты"


@pytest.mark.parametrize(
    "invalid_date", ["2023-01-01-01", 2023, "2023-01-01 01:01:01", 2023.01]
)
def test_invalid_format_date_invalid(invalid_date: str) -> None:
    """Проверяет невалидные форматы сырой строки даты."""
    with pytest.raises(ValueError) as exc_info:
        custom_date(invalid_date)

    assert ERROR_MESSAGE_INVALID__FORMAT_DATE in str(
        exc_info.value
    ), "Ошибка обработки невалидного дня в месяцах"


@pytest.mark.parametrize(
    "current_date, future_date",
    [
        (
            curr_date := datetime.now(),
            curr_date + timedelta(days=1),
        ),
        (
            curr_date := datetime.now(),
            curr_date + timedelta(weeks=1),
        ),
    ],
)
def test_future_date(current_date: datetime, future_date: datetime) -> None:
    """Проверяет даты в будущем."""
    with pytest.raises(ValueError) as exc_info:
        custom_date(future_date)

    assert ERROR_MESSAGE_DATE_IS_FUTURE in str(
        exc_info.value
    ), "Ошибка обработки даты в будущем"
