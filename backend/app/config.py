from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail
from pydantic import SecretStr
from starlette.config import Config
from starlette.datastructures import Secret


config = Config(".env")
PROJECT_NAME = "Visa Document Service"
PROJECT_VERSION = "1.0.0"
API_PREFIX = "/api"

SECRET_KEY = config("SECRET_KEY", cast=Secret)

JWT_ACCESS_TOKEN_EXPIRES_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRES_MINUTES = 15 * 24 * 60  # 15 days
JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_DAYS = 3
JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_MINUTES = JWT_EMAIL_CONFIRMATION_TOKEN_EXPIRES_DAYS * 24 * 60  # 3 days
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
JWT_TOKEN_PREFIX = config("JWT_TOKEN_PREFIX", cast=str, default="Bearer")

mail_config = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_USERNAME", cast=str),
    MAIL_PASSWORD=config("MAIL_PASSWORD", cast=SecretStr),
    MAIL_FROM=config("MAIL_FROM", cast=str),
    MAIL_PORT=config("MAIL_PORT", cast=int, default=1025),
    MAIL_SERVER=config("MAIL_SERVER", cast=str, default="localhost"),
    MAIL_STARTTLS=config("MAIL_STARTTLS", cast=bool, default=False),
    MAIL_SSL_TLS=config("MAIL_SSL_TLS", cast=bool, default=False),
    USE_CREDENTIALS=config("USE_CREDENTIALS", cast=bool, default=False),
    VALIDATE_CERTS=config("VALIDATE_CERTS", cast=bool, default=False),
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates/email'
)
fm_mail = FastMail(mail_config)

FRONTEND_URL = "http://127.0.0.1:8000/"
BACKEND_URL = "http://127.0.0.1:8000/api/"

POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
