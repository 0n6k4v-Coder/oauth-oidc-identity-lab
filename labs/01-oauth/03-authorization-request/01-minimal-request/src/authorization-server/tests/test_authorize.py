from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_minimal_authorization_request() -> None:
    response = client.get(
        "/authorize",
        params={
            "response_type": "code",
            "client_id": "public-client",
            "redirect_uri": "http://localhost:5473/callback",
            "scope": "read",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Authorization Request received",
        "request": {
            "response_type": "code",
            "client_id": "public-client",
            "redirect_uri": "http://localhost:5473/callback",
            "scope": "read",
        },
    }


def test_missing_response_type() -> None:
    response = client.get(
        "/authorize",
        params={
            "client_id": "public-client",
        },
    )

    assert response.status_code == 422


def test_missing_client_id() -> None:
    response = client.get(
        "/authorize",
        params={
            "response_type": "code",
        },
    )

    assert response.status_code == 422