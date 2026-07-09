import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.auth import User
from schemas.auth import UserCreate

logger = logging.getLogger(__name__)


class UserRepository:
    db: Session

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        logger.info("Creating user with repository")
        user = User(username=user_data.username, email=user_data.email, password=user_data.password)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user
    
    def list_users(self):
        users = self.db.scalars(select(User)).all()
        return users