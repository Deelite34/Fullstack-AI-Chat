from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException

from schemas.auth import TokenInput, UserAuthenticate
from services.exceptions import TokenAlreadyBlacklisted


def create_token(auth_service, expires_at: datetime) -> str:
    return jwt.encode(
        {"sub": "123", "exp": expires_at},
        auth_service.config.SECRET_KEY,
        algorithm=auth_service.config.ALGORITHM,
    )


def test_validate_password_returns_user_for_correct_credentials(
    auth_service, user_schema_factory
):
    user_schema = user_schema_factory(
        10, username="auth_valid_user", email="auth_valid@example.com"
    )
    auth_service.user_repository.create_user(user_schema)

    user = auth_service.validate_password(user_schema.username, user_schema.password)

    assert user is not None
    assert user.username == user_schema.username


def test_validate_password_returns_none_for_wrong_password(
    auth_service, user_schema_factory
):
    user_schema = user_schema_factory(
        11, username="auth_invalid_pw", email="auth_invalid_pw@example.com"
    )
    auth_service.user_repository.create_user(user_schema)

    user = auth_service.validate_password(user_schema.username, "wrong-password")

    assert user is None


def test_login_returns_token_for_valid_credentials(auth_service, user_schema_factory):
    user_schema = user_schema_factory(
        12, username="auth_login_user", email="auth_login@example.com"
    )
    auth_service.user_repository.create_user(user_schema)

    token = auth_service.login(
        UserAuthenticate(username=user_schema.username, password=user_schema.password),
    )

    assert token.token_type == "bearer"
    assert token.access_token


def test_login_returns_json_response_for_invalid_password(
    auth_service, user_schema_factory
):
    user_schema = user_schema_factory(
        13, username="auth_bad_password", email="auth_bad_password@example.com"
    )
    auth_service.user_repository.create_user(user_schema)

    with pytest.raises(HTTPException) as excinfo:
        auth_service.login(
            UserAuthenticate(username=user_schema.username, password="wrong-password"),
        )

    assert excinfo.value.status_code == 401
    assert "Invalid username or password" in str(excinfo.value.detail)


def test_login_raises_for_unknown_username(auth_service):
    with pytest.raises(HTTPException) as excinfo:
        auth_service.login(
            UserAuthenticate(username="unknown-user", password="whatever")
        )

    assert excinfo.value.status_code == 401


def test_token_pair_returns_token_for_existing_user(auth_service, user_schema_factory):
    user_schema = user_schema_factory(
        14, username="auth_token_user", email="auth_token@example.com"
    )
    user = auth_service.user_repository.create_user(user_schema)

    token_pair = auth_service.create_jwt_token_pair(user.id)

    access_payload = jwt.decode(
        token_pair[0],
        auth_service.config.SECRET_KEY,
        algorithms=[auth_service.config.ALGORITHM],
    )
    refresh_payload = jwt.decode(
        token_pair[1],
        auth_service.config.SECRET_KEY,
        algorithms=[auth_service.config.ALGORITHM],
    )

    assert access_payload["sub"] == str(user.id)
    assert refresh_payload["sub"] == str(user.id)
    assert access_payload["exp"] > 0
    assert refresh_payload["exp"] > access_payload["exp"]
    assert access_payload["jti"] != refresh_payload["jti"]


def test_verify_token_returns_payload_for_valid_token(
    auth_service, user_schema_factory
):
    user_schema = user_schema_factory(
        15, username="auth_verify_user", email="auth_verify@example.com"
    )
    created_user = auth_service.user_repository.create_user(user_schema)

    token_pair = auth_service.prepare_jwt_tokens(created_user.id)
    payload = auth_service.verify_token(token_pair.access_token)

    assert payload["sub"] == str(created_user.id)
    assert payload["exp"] is not None


def test_verify_token_raises_for_invalid_token(auth_service):
    with pytest.raises(HTTPException) as excinfo:
        auth_service.verify_token("not-a-valid-token")

    assert excinfo.value.status_code == 401


def test_verify_token_raises_for_expired_token(auth_service):
    expired_payload = {
        "sub": "123",
        "exp": datetime.now(UTC) - timedelta(minutes=1),
    }
    expired_token = jwt.encode(
        expired_payload,
        auth_service.config.SECRET_KEY,
        algorithm=auth_service.config.ALGORITHM,
    )

    with pytest.raises(HTTPException) as excinfo:
        auth_service.verify_token(expired_token)

    assert excinfo.value.status_code == 401
    assert "expired" in str(excinfo.value.detail).lower()


def test_logout_blacklists_access_token_when_not_expired(auth_service):
    access_token = create_token(auth_service, datetime.now(UTC) + timedelta(minutes=5))
    expired_refresh_token = create_token(
        auth_service, datetime.now(UTC) - timedelta(minutes=5)
    )

    auth_service.logout(TokenInput(token=access_token), expired_refresh_token)

    assert auth_service.expired_access_tokens_repository.is_blacklisted(access_token)
    assert not auth_service.expired_access_tokens_repository.is_blacklisted(
        expired_refresh_token
    )


def test_logout_blacklists_refresh_token_when_not_expired(auth_service):
    expired_access_token = create_token(
        auth_service, datetime.now(UTC) - timedelta(minutes=5)
    )
    refresh_token = create_token(auth_service, datetime.now(UTC) + timedelta(minutes=5))

    auth_service.logout(TokenInput(token=expired_access_token), refresh_token)

    assert not auth_service.expired_access_tokens_repository.is_blacklisted(
        expired_access_token
    )
    assert auth_service.expired_access_tokens_repository.is_blacklisted(refresh_token)


def test_logout_skips_blacklisting_for_already_expired_tokens(auth_service):
    expired_access_token = create_token(
        auth_service, datetime.now(UTC) - timedelta(minutes=5)
    )
    expired_refresh_token = create_token(
        auth_service, datetime.now(UTC) - timedelta(minutes=5)
    )

    auth_service.logout(TokenInput(token=expired_access_token), expired_refresh_token)

    assert not auth_service.expired_access_tokens_repository.is_blacklisted(
        expired_access_token
    )
    assert not auth_service.expired_access_tokens_repository.is_blacklisted(
        expired_refresh_token
    )


def test_refresh_access_token_returns_new_pair_and_blacklists_old_tokens(
    auth_service, user_schema_factory
):
    user_schema = user_schema_factory(
        16, username="auth_refresh_user", email="auth_refresh@example.com"
    )
    user = auth_service.user_repository.create_user(user_schema)
    old_pair = auth_service.prepare_jwt_tokens(user.id)
    access_payload = auth_service.verify_token(old_pair.access_token)
    refresh_payload = auth_service.verify_token(old_pair.refresh_token)

    new_pair = auth_service.refresh_access_token(
        access_payload,
        refresh_payload,
        TokenInput(token=old_pair.access_token),
        old_pair.refresh_token,
    )

    assert new_pair.token_type == "bearer"
    assert new_pair.access_token != old_pair.access_token
    assert new_pair.refresh_token != old_pair.refresh_token
    assert (
        auth_service.verify_token(new_pair.access_token)["jti"] != access_payload["jti"]
    )
    assert (
        auth_service.verify_token(new_pair.refresh_token)["jti"]
        != refresh_payload["jti"]
    )
    assert auth_service.expired_access_tokens_repository.is_blacklisted(
        old_pair.access_token
    )
    assert auth_service.expired_access_tokens_repository.is_blacklisted(
        old_pair.refresh_token
    )
    assert auth_service.verify_token(new_pair.access_token)["sub"] == str(user.id)
    assert auth_service.verify_token(new_pair.refresh_token)["sub"] == str(user.id)


def test_refresh_access_token_without_access_token_still_rotates_refresh_token(
    auth_service, user_schema_factory
):
    user_schema = user_schema_factory(
        17, username="auth_refresh_cookie_user", email="auth_refresh_cookie@example.com"
    )
    user = auth_service.user_repository.create_user(user_schema)
    old_pair = auth_service.prepare_jwt_tokens(user.id)
    refresh_payload = auth_service.verify_token(old_pair.refresh_token)

    new_pair = auth_service.refresh_access_token(
        None, refresh_payload, None, old_pair.refresh_token
    )

    assert not auth_service.expired_access_tokens_repository.is_blacklisted(
        old_pair.access_token
    )
    assert auth_service.expired_access_tokens_repository.is_blacklisted(
        old_pair.refresh_token
    )
    assert auth_service.verify_token(new_pair.access_token)["sub"] == str(user.id)


def test_verify_token_rejects_blacklisted_token(auth_service, user_schema_factory):
    user_schema = user_schema_factory(
        18, username="auth_blacklisted_user", email="auth_blacklisted@example.com"
    )
    user = auth_service.user_repository.create_user(user_schema)
    access_token = auth_service.prepare_jwt_tokens(user.id).access_token
    payload = auth_service.verify_token(access_token)
    auth_service.blacklist_token(access_token, payload["exp"])

    with pytest.raises(TokenAlreadyBlacklisted):
        auth_service.verify_token(access_token)


def test_authorize_current_user_returns_user_for_valid_access_token(
    auth_service, user_schema_factory
):
    user_schema = user_schema_factory(
        19, username="auth_authorized_user", email="auth_authorized@example.com"
    )
    user = auth_service.user_repository.create_user(user_schema)
    access_token = auth_service.prepare_jwt_tokens(user.id).access_token

    authenticated_user = auth_service.authorize_current_user(access_token)

    assert authenticated_user.id == user.id
    assert authenticated_user.username == user.username


def test_authorize_current_user_rejects_blacklisted_access_token(
    auth_service, user_schema_factory
):
    user_schema = user_schema_factory(
        20, username="auth_revoked_user", email="auth_revoked@example.com"
    )
    user = auth_service.user_repository.create_user(user_schema)
    access_token = auth_service.prepare_jwt_tokens(user.id).access_token
    payload = auth_service.verify_token(access_token)
    auth_service.blacklist_token(access_token, payload["exp"])

    with pytest.raises(HTTPException) as excinfo:
        auth_service.authorize_current_user(access_token)

    assert excinfo.value.status_code == 401


@pytest.mark.parametrize(
    "claims",
    [
        {"exp": datetime.now(UTC) + timedelta(minutes=5)},
        {"sub": "999999", "exp": datetime.now(UTC) + timedelta(minutes=5)},
    ],
    ids=("missing-sub", "unknown-user"),
)
def test_authorize_current_user_rejects_missing_or_unknown_sub(auth_service, claims):
    token = jwt.encode(
        claims,
        auth_service.config.SECRET_KEY,
        algorithm=auth_service.config.ALGORITHM,
    )

    with pytest.raises(HTTPException) as excinfo:
        auth_service.authorize_current_user(token)

    assert excinfo.value.status_code == 401
