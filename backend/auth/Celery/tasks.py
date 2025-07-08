from celery import Celery, shared_task

from backend.auth.Celery.email_service import EmailService
from backend.core.config import settings

celery_app = Celery(
    "worker",
    broker=str(settings.celery.broker_url),
    backend=str(settings.celery.result_backend),
)


@shared_task
def send_confirmation_email_task(
    name_endpoint: str,
    name_message: str,
    email_to: str,
    token: str,
    base_url: str,
) -> None:
    """Задача Celery. Отправляет сообщение пользователю на почту для
    подтверждения регистрации.

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
