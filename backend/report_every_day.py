import logging
from io import BytesIO

import asyncpg
import matplotlib.pyplot as plt
from datetime import date

from backend.core.config import settings


logging.basicConfig(
    format=settings.logging.log_format,
    level=settings.logging.log_level_value,
)

logger = logging.getLogger(__name__)


async def report_stats_every_day():
    dsn = str(settings.db.url).replace("postgresql+asyncpg://", "postgresql://")
    connect = await asyncpg.connect(dsn)

    intervals = [
        (0, 6),
        (6, 12),
        (12, 18),
        (18, 24),
    ]

    result = [
        await connect.fetch(
            f"""SELECT COUNT(*) 
            FROM users 
            WHERE created_at BETWEEN
            CURRENT_DATE + INTERVAL '{start} hours'
            AND CURRENT_DATE + INTERVAL '{end} hours'
            """
        )
        for start, end in intervals
    ]

    categories = ["0-6ч", "6-12ч", "12-18ч", "18-24ч"]

    plt.bar(categories, result, color="#ff7f0e")
    plt.xlabel("Время дня")
    plt.ylabel("Количество зарегистрированных")
    plt.title(f"Регистрации пользователей за: {date.today()}")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    logger.info("Отчет за день построен!")

    return buffer.read()
