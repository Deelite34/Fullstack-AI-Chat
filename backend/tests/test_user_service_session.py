from typing import cast
from types import SimpleNamespace

from sqlalchemy.orm import Session

from schemas.auth import UserReadList
from services.UserService import UserService, get_user_service


def test_get_user_service_uses_the_same_session_for_repository():
    session = cast(Session, object())

    service = get_user_service(session)

    assert isinstance(service, UserService)
    assert service.user_repository.db is session


def test_list_users_returns_wrapped_user_read_list():
    user = SimpleNamespace(id=1, username="alice", email="alice@example.com")
    service = UserService(user_repository=SimpleNamespace(list_users=lambda: [user]))

    response = service.list_users()

    assert isinstance(response, UserReadList)
    assert response.users[0].username == "alice"
