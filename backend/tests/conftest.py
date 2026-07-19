import logging
from uuid import uuid4

import pytest
from typing import Iterator
from sqlalchemy.orm import Session, sessionmaker
from services.user_service import get_user_service
from services.auth_service import get_auth_service
from schemas.auth import UserCreate
from repositories.users import UserRepository
from config.settings import config
from db import Base
from sqlalchemy import create_engine


logger = logging.getLogger(__name__)

test_db_url = config.test_db_url
engine = create_engine(test_db_url)
db_session = sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture()
def test_db() -> Iterator[Session]:
    """Create db tables, return a test db session, and clean up afterwards."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = db_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def user_repository(test_db):
    return UserRepository(test_db)


@pytest.fixture()
def user_service(test_db):
    return get_user_service(test_db)


@pytest.fixture()
def auth_service(test_db):
    return get_auth_service(test_db)


@pytest.fixture()
def user_schema_factory():
    """
    Returns user schema factory function
    that allows to create schema for specific user
    """

    def make_user_schema(id: int, username: str = "", email: str = ""):
        return UserCreate(
            username=username or f"testuser-{id}",
            email=email or f"test_email_{id}@test.com",
            password="test_password",
        )

    return make_user_schema


@pytest.fixture()
def random_user_schema():
    """Generate schema for random user"""
    return UserCreate(
        username="testuser-" + str(uuid4()),
        email=f"test_email_{str(uuid4())}@test.com",
        password="test_password",
    )
