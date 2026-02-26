import logging
from pathlib import Path
from typing import ClassVar, Literal
from datetime import datetime

from fastapi.templating import Jinja2Templates
from pydantic import (
    AmqpDsn,
    BaseModel,
    EmailStr,
    Field,
    PostgresDsn,
    RedisDsn,
    SecretStr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.utils.date_filter_style import custom_filters

BASE_DIR = Path(__file__).resolve().parent.parent.parent

TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_PATH_TO_AVATAR = "/client_files/avatars/дефолтный_аватар.jpg"

type SMTPUser = EmailStr
type TaskRoute = dict[str, str]
type TaskRoutes = dict[str, TaskRoute]
type Algorithm = Literal[
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
    "ES256",
]
type LogLevel = Literal[
    "debug",
    "info",
    "warning",
    "error",
    "critical",
]


class JwtConfig(BaseModel):
    secret_key: SecretStr
    algorithm: Algorithm
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


class LoggingConfig(BaseModel):
    log_level: LogLevel = "info"
    log_format: str = LOG_DEFAULT_FORMAT

    @property
    def log_level_value(self) -> int:
        """Функция для получения значения уровня логирования."""
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class Jinja2Settings(BaseModel):
    template_dir: ClassVar[Jinja2Templates] = Jinja2Templates(TEMPLATES_DIR)

    def model_post_init(self, __context: object) -> None:
        """Специальная функция Pydantic, которая автоматически вызывается при
        инициализации модели, и вызывает функцию configure_templates для
        настройки шаблонов Jinja2."""

        self.configure_templates()

    @classmethod
    def configure_templates(cls) -> None:
        """Функция для настройки шаблонов Jinja2.

        - Добавляет фильтр для форматирования даты.
        - Добавляет глобальную переменную для текущего пользователя,
          чтобы шаблоны, где нет аутентифицированного пользователя,
          мог посещать сайт, так как current_user обязателен для base.html
        """

        cls.template_dir.env.filters.update(custom_filters)
        cls.template_dir.env.globals["current_user"] = None


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    MODE: str = "TEST"


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int


class CeleryConfig(BaseModel):
    broker_url: AmqpDsn
    result_backend: RedisDsn
    task_routes: TaskRoutes = Field(
        default_factory=lambda: {"app.tasks.*": {"queue": "email_tasks"}},
        description="Routing configuration for Celery tasks",
    )


class SMTPSettings(BaseModel):
    host: str
    port: int
    user: SMTPUser
    password: SecretStr
    use_tls: bool = True
    use_ssl: bool = False


class ChatMessage(BaseModel):
    dialog_id: int
    sender_id: int
    text: str
    created_at: datetime


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".test.env",
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
            # порядок важен, т.к. pydantic_settings отдаёт приоритет
            # последнеиу файлу, и если последний файл это не продакшн,
            # .env то найстройки будут искаться в .env.template
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    jwt: JwtConfig = Field(default_factory=JwtConfig)
    templates: Jinja2Settings = Field(default_factory=Jinja2Settings)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    celery: CeleryConfig = Field(default_factory=CeleryConfig)
    smtp: SMTPSettings = Field(default_factory=SMTPSettings)
    msg: type[ChatMessage] = ChatMessage

    db: DatabaseConfig


CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

settings = Settings()
