from backend.auth.Celery.email_service import EmailService
from backend.core.config import settings
from celery import Celery, shared_task


celery_app = Celery(
    "worker", broker=settings.celery.broker_url, backend=settings.celery.result_backend
)


@shared_task
def send_confirmation_email_task(
    name_endpoint: str, name_message: str, email_to: str, token: str, base_url: str
):
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


# @shared_task
# async def delete_unconfirmed_user_task(token: str) -> bool:
#     """
#     Задача Celery. Удаляет созданную запись в редис, если пользователь не перешел по ссылке в письме
#     в течение 30 минут (по умолчанию)
#
#     :param token: Token созданный для письма регистрации
#     :return:
#     """
#     arc = AsyncRedisClient()
#
#     user_token = await arc.token_exists(token)
#     if user_token:
#         await arc.delete_pending_token(token)
#         return True
#     return False
