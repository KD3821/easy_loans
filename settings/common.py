import os
from pathlib import Path

import dotenv

path_to_env = Path(__file__).parents[1].joinpath(".env")

try:
    dotenv.read_dotenv(path_to_env)
except AttributeError:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=path_to_env)

PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
ADMIN_PORT = int(os.environ.get("ADMIN_PORT", 5000))
ADMIN_HOST = os.environ.get("ADMIN_HOST", "0.0.0.0")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ENV = os.environ.get("ENV")

DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_PORT = int(os.environ.get("DB_PORT"))

LOGURU_BACKTRACE = True
LOGURU_DIAGNOSE = True
LOG_LEVEL = "INFO"
LOGURU_FORMAT = (
    "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>]"
    "[<level>{level}</level>] "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>\n"
)

AUTH_SECRET_KEY = os.environ.get("AUTH_SECRET_KEY")
AUTH_HASHING_ALGORITHM = "HS256"
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES")
)
AUTH_REFRESH_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("AUTH_REFRESH_TOKEN_EXPIRE_MINUTES")
)

APP_VERSION = "0.1"
APP_API_NAME = "Python Template API"
APP_ADMIN_NAME = "Python Template Admin"

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
AMQP_DSN = os.environ.get("AMQP_DSN")
