import pytest
from fastapi.testclient import TestClient

from db import get_session
from main import create_app


@pytest.mark.parametrize("path", ("/api/stream", "/api/stream/debug"))
@pytest.mark.parametrize(
    "authorization",
    (None, "Bearer forged-or-invalid-token"),
    ids=("missing-token", "invalid-token"),
)
def test_chat_stream_endpoints_reject_direct_unauthenticated_requests(
    test_db, path, authorization
):
    app = create_app()

    def override_get_session():
        return test_db

    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as client:
            headers = (
                {"Authorization": authorization} if authorization is not None else None
            )
            response = client.post(
                path, json={"chat_text": "hello"}, headers=headers
            )
            assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()
