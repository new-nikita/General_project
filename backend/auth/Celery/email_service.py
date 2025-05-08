import logging
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urljoin

from backend.core.config import settings

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис отправки писем"""

    @staticmethod
    def build_confirmation_link(base_url: str, token: str) -> str:
        """
        :param base_url:
        :param token: созданный токен пользователя для авторизации
        :return: возвращает готовую ссылку
        """
        url = urljoin(base_url, f"/confirm?token={token}")

        # url = f"{base_url.rstrip('/')}/confirm?token={token}"
        logger.info(f"Cсылка с ТОКЕНом создана \n {url}")

        return url
        # f"{base_url.rstrip('/')}/confirm?token={token}" # rstrip('/') убирает лишний /, если base_url уже заканчивается на слэш.

    @staticmethod
    def compose_email(to_email: str, confirm_link: str) -> str:
        """

        :param to_email: Почта введенная пользователем
        :param confirm_link: Ссылка подтверждения
        :return: возвращает готовое сообщение для отправки
        """
        message = MIMEMultipart()
        message["Subject"] = "Подтвердите почту"
        message["From"] = settings.smtp.user
        logger.info("С почты %s", settings.smtp.user)
        message["To"] = to_email
        logger.info("на почту %s", to_email)

        message.attach(
            MIMEText(
                f"Перейдите по ссылке для подтверждения почты: {confirm_link}", "plain"
            )
        )

        logger.info("Сообщение сконфигурировано!")
        message = message.as_string()
        return message

    @staticmethod
    def send_email(message: str, to_email: str):

        try:
            logger.info("Захожу в отправку письма")
            with smtplib.SMTP(settings.smtp.host, settings.smtp.port) as server:
                server.ehlo()
                server.starttls()
                server.login(settings.smtp.user, settings.smtp.password)

                server.sendmail(
                    from_addr=settings.smtp.user,
                    to_addrs=to_email,
                    msg=message,
                )
            logger.info("Сообщение отправлено на почту")
        except Exception as e:
            logger.error(f"Ошибка при отправке письма: {e}")
