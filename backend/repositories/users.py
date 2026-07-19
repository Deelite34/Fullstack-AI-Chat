import logging
from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy import or_, select

from services.exceptions import CredentialsAlreadyUsed
from repositories.base import BaseRepository
from models.auth import User
from schemas.auth import UserCreate

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    def __init__(self, *args):
        super().__init__(*args)

    def create_user(self, user_data: UserCreate) -> User:
        if self.db.scalars(
            select(User).filter(
                or_(User.username == user_data.username, User.email == user_data.email)
            )
        ).first():
            raise CredentialsAlreadyUsed("This username or email is not available.")

        user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self) -> Sequence[User]:
        return self.db.scalars(select(User)).all()

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalars(select(User).where(User.email == email)).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalars(select(User).where(User.username == username)).first()

    def check_user_by_username_exists(self, username: str) -> User | None:
        """return True if user exists or False otherwise"""
        return self.get_by_username(username)

    def check_user_by_email_exists(self, email: str) -> User | None:
        """return True if user exists or False otherwise"""
        return self.get_by_email(email)
