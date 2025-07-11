import logging
from io import BytesIO

import asyncpg
import matplotlib.pyplot as plt
import matplotlib
from datetime import date

from backend.core.config import settings


logging.basicConfig(
    format=settings.logging.log_format,
    level=settings.logging.log_level_value,
)

logger = logging.getLogger(__name__)


async def report_statistic_every_day():
    dsn = str(settings.db.url).replace(
        "postgresql+asyncpg://",
        "postgresql://",
    )
    connect = await asyncpg.connect(dsn)

    intervals = [
        (0, 6),
        (6, 12),
        (12, 18),
        (18, 24),
    ]

    raw_result = [
        await connect.fetch(
            """SELECT COUNT(*) 
            FROM users 
            WHERE created_at BETWEEN
            CURRENT_DATE + $1::inteerval
            AND CURRENT_DATE + $2::inteerval
            """,
            start,
            end,
        )
        for start, end in intervals
    ]

    result = [record[0]["count"] for record in raw_result]

    print(result)

    categories = ["0-6ч", "6-12ч", "12-18ч", "18-24ч"]

    matplotlib.use("Agg")

    bars = plt.bar(categories, result, color="#ff7f0e")
    plt.xlabel("Время дня")
    plt.ylabel("Количество зарегистрированных")
    plt.title(f"Регистрации пользователей за: {date.today()}")

    for number, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # x-координата (центр столбца)
            height / 2,  # y-координата (середина столбца)
            result[number] if result[number] > 0 else None,  # текст (значение)
            ha="center",
            va="center",
            color="black",
            fontsize=12,
        )

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    logger.info("Отчет за день построен!")

    return buffer.read()
