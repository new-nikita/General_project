import asyncio

from celery.schedules import crontab

from backend.auth.Celery.email_service import EmailService
from backend.core.config import settings
from celery import Celery, shared_task
from backend.report_every_day import report_statistic_every_day


app = Celery(
    "worker",
    broker=str(settings.celery.broker_url),
    backend=str(settings.celery.result_backend),
)

app.conf.beat_schedule = {
    "task_report_statistic_every_day": {
        "task": "tasks.report_statistic_every_day",
        "schedule": crontab(minute=0, hour=0),
    }
}


@shared_task
def send_confirmation_email_task(
    name_endpoint: str,
    name_message: str,
    email_to: str,
    token: str,
    base_url: str,
) -> None:
    """
    Задача Celery. Отправляет сообщение пользователю на почту для подтверждения регистрации.

    :param name_endpoint: Имя эндоинта для генерации валидной ссылки
    :param name_message: Имя шаблона для генерации валидной ссылки
    :param email_to: Email полученный от пользователя в form_data
    :param token: Token созданный для письма регистрации
    :param base_url: Базовая ссылка проекта
    :return:
    """
    link = EmailService.build_confirmation_link(name_endpoint, base_url, token)
    message = EmailService.compose_email(name_message, email_to, link)
    EmailService.send_email(message, email_to)


@shared_task(name="tasks.report_statistic_every_day")
def sending_statistic_to_the_email() -> None:
    """ОтправлЯкет отчет по зарегистрированным пользователям каждый день."""
    result_statistic = asyncio.run(report_statistic_every_day())
    message = EmailService.statistics_message_configuration(result_statistic)
    EmailService.sending_a_message_from_statistic(message)
