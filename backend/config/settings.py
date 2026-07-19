from datetime import timedelta
from functools import lru_cache
import os


class Config:
    # Jwt settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretvalue")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    REFRESH_TOKEN_EXPIRES = timedelta(days=1)

    DEBUG = True
    LOG_LEVEL = os.getenv("LOG_LEVEL")

    APP_DB_USER = os.environ.get("APP_DB_USER")
    APP_DB_PASSWORD = os.environ.get("APP_DB_PASSWORD")
    APP_DB_NAME = os.environ.get("APP_DB_NAME")
    APP_DB_HOSTNAME = os.environ.get("APP_DB_HOSTNAME")

    TEST_APP_DB_USER = os.environ.get("TEST_APP_DB_USER")
    TEST_APP_DB_PASSWORD = os.environ.get("TEST_APP_DB_PASSWORD")
    TEST_APP_DB_NAME = os.environ.get("TEST_APP_DB_NAME")
    TEST_APP_DB_HOSTNAME = os.environ.get("TEST_APP_DB_HOSTNAME")

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "()": "uvicorn.logging.DefaultFormatter",
                "format": "{levelprefix} [{name}] {message}",  # 'context' key in extra parameter of logging
                "datefmt": "%d %H:%M:%S",
                "style": "{",
                "use_colors": True,
            },
            "detailed": {
                "()": "uvicorn.logging.DefaultFormatter",
                "format": "{levelprefix} [{name}] {message}\t {filename}-{lineno}:[{asctime}]",
                "datefmt": "%d %H:%M:%S",
                "style": "{",
                "use_colors": True,
            },
        },
        "handlers": {
            "console": {
                "level": LOG_LEVEL,
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "root": {
                "handlers": ["console"],
                "level": LOG_LEVEL,
                "propagate": False,
            },
        },
    }
    DB_ECHO = True

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "test_key")

    # TODO: check later best way to set this up, at least for local development
    cors_origins = []

    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_MAX_CONN_RETRIES = 3

    AIService = "langchain-ollama"
    OLLAMA_ROOT_URL = "http://ollama:11434"
    OLLAMA_URL = f"{OLLAMA_ROOT_URL}/api/chat"
    MODEL_PROVIDER = "ollama"
    OLLAMA_MODEL = "llama3.2"
    OLLAMA_SYSTEM_PROMPT = "Limit your responses to maximum of 500 characters."

    @property
    def db_url(self) -> str:
        return f"postgresql://{self.APP_DB_USER}:{self.APP_DB_PASSWORD}@{self.APP_DB_NAME}:5432/{self.APP_DB_HOSTNAME}"

    @property
    def test_db_url(self) -> str:
        return f"postgresql://{self.TEST_APP_DB_USER}:{self.TEST_APP_DB_PASSWORD}@{self.TEST_APP_DB_NAME}:5433/{self.TEST_APP_DB_HOSTNAME}"


@lru_cache
def get_config() -> Config:
    return Config()


config = get_config()
