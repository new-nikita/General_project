import logging
import smtplib
from email.message import EmailMessage
from email.mime.image import MIMEImage
from urllib.parse import urljoin

from backend.core.config import settings

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис отправки писем."""

    @staticmethod
    def build_confirmation_link(
        name_endpoint: str,
        base_url: str,
        token: str,
        client: str | None = None,
    ) -> str:
        """Создает валидную ссылку с токеном."""
        if client == "mobile":
            url = f"generalproject://register?token={token}"
        else:
            url = urljoin(base_url, f"/{name_endpoint}?token={token}")
        logger.info("Ссылка с токеном создана: %s", url)
        return url

    @staticmethod
    def compose_email(
        name_message: str,
        to_email: str,
        confirm_link: str,
    ) -> EmailMessage:
        """Создает сообщение EmailMessage с подтверждением."""
        message = EmailMessage()
        message["Subject"] = "Подтвердите почту"
        message["From"] = settings.smtp.user
        message["To"] = to_email

        text = f"Пожалуйста, подтвердите свою почту, перейдя по ссылке:\n{confirm_link}"
        # html = settings.templates.template_dir.get_template(
        #     f"info/{name_message}.html"
        # ).render(confirm_link=confirm_link)

        message.set_content(text)
        # message.add_alternative(html, subtype="html")

        logger.info("Email-сообщение собрано.")
        return message

    @staticmethod
    def send_email(message: EmailMessage, to_email: str) -> bool:
        """Отправка email сообщения."""
        smtp_obj = None
        try:
            logger.info("Попытка подключения к SMTP серверу...")
            smtp_obj = smtplib.SMTP(settings.smtp.host, settings.smtp.port)
            smtp_obj.ehlo()
            if settings.smtp.use_tls:
                logger.debug("Инициализация TLS...")
                smtp_obj.starttls()
                smtp_obj.ehlo()
            smtp_obj.login(
                settings.smtp.user,
                settings.smtp.password.get_secret_value(),
            )
            smtp_obj.send_message(message)
            logger.info("Письмо успешно отправлено на %s", to_email)
            return True
        except Exception as e:
            logger.error("Ошибка при отправке письма: %s", e)
            return False
        finally:
            if smtp_obj:
                smtp_obj.quit()

    @staticmethod
    def statistics_message_configuration(statistic: bytes) -> EmailMessage:
        """
        Создает сообщение статистики
        """
        message = EmailMessage()
        message["Subject"] = "Статистика регистраций"
        message["From"] = settings.smtp.user
        message["To"] = settings.smtp.user_to_email

        text = "Статистика по зарегистрированным пользователям за последние сутки"
        message.set_content(text)

        image = MIMEImage(statistic, _subtype="png")
        image.add_header(
            "Content-Disposition",
            "attachment",
            filename="statistic.png",
        )

        message.add_attachment(
            image.get_payload(decode=True),
            maintype="image",
            subtype="png",
            filename="statistic.png",
        )

        logger.info("Email-сообщение статистики собрано.")
        return message

    @staticmethod
    def sending_a_message_from_statistic(message: EmailMessage) -> None:
        """
        Отправка email сообщения статистики
        """
        smtp_obj = None
        try:
            logger.info("Попытка подключения к SMTP серверу...")
            smtp_obj = smtplib.SMTP(settings.smtp.host, settings.smtp.port)
            smtp_obj.ehlo()
            if settings.smtp.use_tls:
                logger.debug("Инициализация TLS...")
                smtp_obj.starttls()
                smtp_obj.ehlo()
            smtp_obj.login(settings.smtp.user, settings.smtp.password)
            smtp_obj.send_message(message)
            logger.info("Письмо статистики успешно отправлено")
        except Exception as e:
            logger.error("Ошибка при отправке письма: %s", e)
        finally:
            if smtp_obj:
                smtp_obj.quit()
