import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from config.settings import Config, config
from db import get_session
from repositories.users import UserRepository
from schemas.auth import UserCreate, UserRead, UserReadList


logger = logging.getLogger()


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.config: Config = config
        self.user_repository: UserRepository = user_repository

    def create_user(self, user: UserCreate) -> UserRead:
        new_user = self.user_repository.create_user(user)
        return UserRead.model_validate(new_user)
    
    def list_users(self) -> UserReadList:
        users = self.user_repository.list_users()
        user_reads = [UserRead.model_validate(user) for user in users]
        return UserReadList(users=user_reads)


def get_user_service(
    session: Annotated[Session, Depends(get_session)]
) -> UserService:
    return UserService(UserRepository(session))