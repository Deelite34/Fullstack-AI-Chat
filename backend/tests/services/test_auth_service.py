from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse

from schemas.auth import UserAuthenticate


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
        result = auth_service.login(
            UserAuthenticate(username=user_schema.username, password="wrong-password"),
        )

    assert excinfo.__dict__["_excinfo"][0] is HTTPException
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

    assert isinstance(token_pair, tuple)
    assert token_pair


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
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
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
