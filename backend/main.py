import logging
import logging.config

from config.settings import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chat import llm_router
from routers.auth import auth_router

def configure_logging():
    logging.config.dictConfig(config.LOGGING_CONFIG)


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(llm_router)
    app.include_router(auth_router)

    return app


app = create_app()
