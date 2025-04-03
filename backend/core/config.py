import logging
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic import PostgresDsn
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

DATABASE_URL = os.getenv("APP_CONFIG__DB__URL")
SECRET_KEY = os.getenv("SECRET_KEY")


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


class DatabaseConfig(BaseModel):
    url: PostgresDsn = DATABASE_URL
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        )
    )
    logging: LoggingConfig = LoggingConfig()
    db: DatabaseConfig = DatabaseConfig()
    jwt: JwtConfig = JwtConfig()
    template_dir: Path = TEMPLATES_DIR


CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

settings = Settings()
