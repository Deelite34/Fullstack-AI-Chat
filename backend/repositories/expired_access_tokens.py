import logging
from datetime import UTC, datetime

from models.auth import ExpiredAccessTokens
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ExpiredTokenRepository(BaseRepository):
    def __init__(self, *args):
        super().__init__(*args)

    def is_blacklisted(self, token: str):
        """Check if token is blacklisted by checking if it exists in the expired tokens table"""
        return (
            self.db.query(ExpiredAccessTokens).filter_by(token=token).first()
            is not None
        )

    def blacklist_token(self, token: str, expire_time: int | float):
        expire_datetime = datetime.fromtimestamp(expire_time, tz=UTC)
        expired_token = ExpiredAccessTokens(token=token, expire_time=expire_datetime)
        self.db.add(expired_token)
        self.db.commit()

    def expired_token_cleanup(self):
        """
        Remove tokens from table, that would be expired on current time
        params:
            commit: bool - if True, commit changes to database
        """
        current_time = datetime.now(UTC)
        self.db.query(ExpiredAccessTokens).filter(
            ExpiredAccessTokens.expire_time < current_time
        ).delete()
        self.db.commit()
