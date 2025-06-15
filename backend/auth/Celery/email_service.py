import logging
import smtplib
from email.message import EmailMessage
from urllib.parse import urljoin

from fastapi.templating import Jinja2Templates

from backend.core.config import settings, TEMPLATES_DIR

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)

logger = logging.getLogger(__name__)

# templates = Jinja2Templates(directory=TEMPLATES_DIR / "info")


class EmailService:
    """Сервис отправки писем"""

    @staticmethod
    def build_confirmation_link(
        name_endpoint: str,
        base_url: str,
        token: str,
    ) -> str:
        """
        Создает валидную ссылку с токеном
        """
        url = urljoin(base_url, f"/{name_endpoint}?token={token}")
        logger.info(f"Ссылка с токеном создана: {url}")
        return url

    @staticmethod
    def compose_email(
        name_message: str,
        to_email: str,
        confirm_link: str,
    ) -> EmailMessage:
        """
        Создает сообщение EmailMessage с подтверждением
        """
        message = EmailMessage()
        message["Subject"] = "Подтвердите почту"
        message["From"] = settings.smtp.user
        message["To"] = to_email

        text = f"Пожалуйста, подтвердите свою почту, перейдя по ссылке:\n{confirm_link}"

        # html = templates.get_template(f"{name_message}.html").render(
        #     confirm_link=confirm_link
        # )
        html = settings.templates.template_dir.get_template(
            f"info/{name_message}.html"
        ).render(confirm_link=confirm_link)

        message.set_content(text)
        message.add_alternative(html, subtype="html")

        logger.info("Email-сообщение собрано.")
        return message

    @staticmethod
    def send_email(message: EmailMessage, to_email: str) -> bool:
        """
        Отправка email сообщения
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
            logger.info(f"Письмо успешно отправлено на {to_email}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке письма: {e}")
            return False
        finally:
            if smtp_obj:
                smtp_obj.quit()
