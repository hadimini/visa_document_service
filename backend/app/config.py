from starlette.config import Config
from starlette.datastructures import Secret


config = Config(".env")
PROJECT_NAME = "Visa Document Service"
PROJECT_VERSION = "1.0.0"
API_PREFIX = "/api"

SECRET_KEY = config("SECRET_KEY", cast=Secret)

JWT_ACCESS_TOKEN_EXPIRES_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRES_MINUTES = 15 * 24 * 60  # 15 days
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
# JWT_AUDIENCE = config("JWT_AUDIENCE", cast=str, default="vs:auth")
JWT_TOKEN_PREFIX = config("JWT_TOKEN_PREFIX", cast=str, default="Bearer")

POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
