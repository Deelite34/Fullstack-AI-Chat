import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from services.exceptions import CredentialsAlreadyUsed
from db import get_session
from repositories.users import UserRepository
from schemas.auth import UserCreate, UserRead, UserReadList


logger = logging.getLogger()


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository: UserRepository = user_repository

    def create_user(self, user: UserCreate) -> UserRead:
        # Check if username or email are already taken
        existing_user_by_username = self.user_repository.check_user_by_username_exists(
            user.username
        )
        existing_user_by_email = self.user_repository.check_user_by_email_exists(
            user.email
        )
        if existing_user_by_username or existing_user_by_email:
            raise CredentialsAlreadyUsed("This username or email is not available.")

        new_user = self.user_repository.create_user(user)
        return UserRead.model_validate(new_user)

    def list_users(self) -> UserReadList:
        users = self.user_repository.list_users()
        user_reads = [UserRead.model_validate(user) for user in users]
        return UserReadList(users=user_reads)

    def get_user_by_id(self, user_id: int) -> UserRead | None:
        user = self.user_repository.get_by_id(user_id)
        if user:
            return UserRead.model_validate(user)
        return None

    def get_user_by_username(self, username) -> UserRead | None:
        user = self.user_repository.get_by_username(username)
        if user:
            return UserRead.model_validate(user)
        return None


def get_user_service(session: Annotated[Session, Depends(get_session)]) -> UserService:
    """Return user service with db session object dependency injected"""
    return UserService(UserRepository(session))
