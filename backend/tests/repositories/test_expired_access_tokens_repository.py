from datetime import UTC, datetime

from models.auth import ExpiredAccessTokens
from repositories.expired_access_tokens import ExpiredTokenRepository


def test_blacklist_token_persists_token_with_expiry(test_db):
    expires_at = 1794577660
    repository = ExpiredTokenRepository(test_db)

    repository.blacklist_token("token-to-blacklist", expires_at)

    stored_token = (
        test_db.query(ExpiredAccessTokens)
        .filter_by(token="token-to-blacklist")
        .one()
    )
    assert stored_token.expire_time == datetime.fromtimestamp(expires_at, tz=UTC)
