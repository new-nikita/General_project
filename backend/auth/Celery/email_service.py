from core.config import settings
from email.message import EmailMessage
import logging
import smtplib
from urllib.parse import urljoin

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
        logger.info('Cсылка с ТОКЕНом создана')

        return url
            # f"{base_url.rstrip('/')}/confirm?token={token}" # rstrip('/') убирает лишний /, если base_url уже заканчивается на слэш.



    @staticmethod
    def compose_email(to_email: str, confirm_link: str) -> EmailMessage:
        """

        :param to_email: Почта введенная пользователем
        :param confirm_link: Ссылка подтверждения
        :return: возвращает готовое сообщение для отправки
        """
        message = EmailMessage()
        message["Subject"] = "Подтвердите почту"
        message["From"] = settings.smtp.user  # Используем тот же email, что и SMTP логин
        message["To"] = to_email
        message.set_content(f"Перейдите по ссылке для подтверждения почты: {confirm_link}")

        logger.info('Сообщение сконфигурировано!')

        return message


    @staticmethod
    def send_email(message: EmailMessage, to_email: str):
        try:
            logger.info('Захожу в отправку письма')
            smtpObj = smtplib.SMTP(settings.smtp.host, settings.smtp.port)
            smtpObj.ehlo()
            smtpObj.starttls()
            smtpObj.login(settings.smtp.user, settings.smtp.password)
            smtpObj.sendmail("nikita.popkov.docker@gmail.com","nik.popkov.98@list.ru","go to bed!")
            logger.info('Сообщение отправлено на почту')
        except Exception as e:
            logger.error(f"Ошибка при отправке письма: {e}")
        finally:
            smtpObj.quit()


