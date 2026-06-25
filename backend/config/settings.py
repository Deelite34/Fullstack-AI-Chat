import os


class Config:
    LOG_LEVEL = os.getenv("LOG_LEVEL")

    APP_DB_USER = os.environ.get("APP_DB_USER")
    APP_DB_PASSWORD = os.environ.get("APP_DB_PASSWORD")
    APP_DB_NAME = os.environ.get("APP_DB_NAME")
    APP_DB_HOSTNAME = os.environ.get("APP_DB_HOSTNAME")

    DATABASE_URL = "postgresql://{}:{}@{}:5432/{}".format(
        APP_DB_USER,
        APP_DB_PASSWORD,
        APP_DB_NAME,
        APP_DB_HOSTNAME,
    )

    APP_DB_TEST_USER = os.environ.get("APP_DB_TEST_USER")
    APP_DB_TEST_PASSWORD = os.environ.get("APP_DB_TEST_PASSWORD")
    APP_DB_TEST_NAME = os.environ.get("APP_DB_TEST_NAME")
    APP_DB_TEST_HOSTNAME = os.environ.get("APP_DB_TEST_HOSTNAME")

    TEST_DATABASE_URL = "postgresql://{}:{}@{}:5433/{}".format(
        APP_DB_TEST_USER,
        APP_DB_TEST_PASSWORD,
        APP_DB_TEST_NAME,
        APP_DB_TEST_HOSTNAME,
    )

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "()": "uvicorn.logging.DefaultFormatter",
                "format": "{levelprefix} [{name}] {message}",
                "datefmt": "%d %H:%M:%S",
                "style": "{",
                "use_colors": True,
            },
            "detailed": {
                "()": "uvicorn.logging.DefaultFormatter",
                "format": "{levelprefix} [{name}] {message}\t {filename}-{lineno}:[{asctime}]",  # thread number, time etc can be present here
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
    DB_ECHO = False

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "test_key")

    cors_origins = ["*"]

    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_MAX_CONN_RETRIES = 3

    AIService = "langchain-ollama"
    OLLAMA_ROOT_URL = "http://ollama:11434"
    OLLAMA_URL = f"{OLLAMA_ROOT_URL}/api/chat"
    MODEL_PROVIDER = "ollama"
    OLLAMA_MODEL = "llama3.2"
    OLLAMA_SYSTEM_PROMPT = "Limit your responses to maximum of 500 characters."
