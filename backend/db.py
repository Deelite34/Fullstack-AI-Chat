import logging
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config.settings import config

engine = create_engine(config.db_url, echo=True)
db_session = sessionmaker(bind=engine)
Base = declarative_base()

logger = logging.getLogger(__name__)


def get_session() -> Generator[Session]:
    session = db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        logger.info("closing session in get_session func")
        session.close()
