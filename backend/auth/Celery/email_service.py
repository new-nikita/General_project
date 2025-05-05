from celery import Celery
from core.config import settings

from email.message import EmailMessage

from auth.tokens_service import TokenService

import smtplib
import ssl

class EmailService:
    """Сервис отправки писем"""

    @staticmethod
    def build_confirmation_link(base_url: str, token: str) -> str:
        """

        :param base_url:
        :param token:
        :return:
        """
        return f"{base_url.rstrip('/')}/confirm?token={token}"

    @staticmethod
    def compose_email(to_email: str, confirm_link: str) -> EmailMessage:
        """

        :param to_email:
        :param confirm_link:
        :return:
        """
        message = EmailMessage()
        message["Subject"] = "Подтвердите почту"
        message["From"] = settings.smtp.user  # Используем тот же email, что и SMTP логин
        message["To"] = to_email
        message.set_content(f"Перейдите по ссылке для подтверждения почты: {confirm_link}")
        return message


    @staticmethod
    def send_email(message: EmailMessage):
        context = ssl.create_default_context()
        if settings.smtp.use_ssl:
            with smtplib.SMTP_SSL(settings.smtp.host, settings.smtp.port, context=context) as server:
                server.login(settings.smtp.user, settings.smtp.password)
                server.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp.host, settings.smtp.port) as server:
                if settings.smtp.use_tls:
                    server.starttls(context=context)
                server.login(settings.smtp.user, settings.smtp.password)
                server.send_message(message)


