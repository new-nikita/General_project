import logging
import os
from pathlib import Path
from typing import Literal, ClassVar

from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, PostgresDsn, AnyUrl, RedisDsn

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from dotenv import find_dotenv, load_dotenv

if find_dotenv():
    load_dotenv()  # take environment variables from.env.
else:
    raise RuntimeError("Couldn't find .env file")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR.parent / "frontend" / "templates"

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

SECRET_KEY = os.getenv("SECRET_KEY", "test_secret_key")


class JwtConfig(BaseModel):
    secret_key: str = SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class Jinja2Settings(BaseModel):
    template_dir: ClassVar[Jinja2Templates] = Jinja2Templates(TEMPLATES_DIR)
    template_dir.env.globals["current_user"] = None


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    MODE: str = "TEST"


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class CeleryConfig(BaseModel):
    # broker_url: AnyUrl = "redis://localhost:6379/0"  #  REDIS
    broker_url: AnyUrl = "pyamqp://guest:guest@localhost//"  # AMQP (RabbitMQ)
    result_backend: RedisDsn = "redis://localhost:6379/0"
    task_routes: dict[str, dict[str, str]] = {"app.tasks.*": {"queue": "email_tasks"}}


class SMTPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=( BASE_DIR / ".env"),
        env_prefix="SMTP_",
    )
    host: str
    port: int
    user: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
            BASE_DIR / ".test.env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    logging: LoggingConfig = LoggingConfig()
    jwt: JwtConfig = JwtConfig()
    templates: Jinja2Settings = Jinja2Settings()
    redis: RedisConfig = RedisConfig()
    celery: CeleryConfig = CeleryConfig()
    smtp: SMTPSettings = SMTPSettings()
    db: DatabaseConfig


CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

settings = Settings()
