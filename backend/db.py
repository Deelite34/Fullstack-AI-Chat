from collections.abc import Generator
import logging

from config.settings import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker


engine = create_engine(config.get_db_url)
db_session = sessionmaker(bind=engine)
Base = declarative_base()

logger = logging.getLogger(__name__)

def get_session() -> Generator[Session, None, None]:
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
