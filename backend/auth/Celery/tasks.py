from auth.Celery.email_service import EmailService
from core.config import settings
from celery import Celery
from auth.redis_client import AsyncRedisClient

celery_app = Celery("worker", broker=settings.celery.broker_url, backend=settings.celery.result_backend)

@celery_app.task
def send_confirmation_email_task(email_to: str, token: str, base_url: str):
    link = EmailService.build_confirmation_link(base_url, token)
    message = EmailService.compose_email(email_to, link)
    EmailService.send_email(message)

@celery_app.task
def delete_unconfirmed_user_task(token: str) -> bool:
    user_token = AsyncRedisClient.token_exists(token)
    if user_token:
        AsyncRedisClient.delete_pending_token(token)
        return True
    return False