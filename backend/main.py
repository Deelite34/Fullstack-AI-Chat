import logging
import logging.config

from config.settings import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chat import llm_router


def configure_logging():
    logging.config.dictConfig(Config.LOGGING_CONFIG)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(llm_router)

    return app


app = create_app()
