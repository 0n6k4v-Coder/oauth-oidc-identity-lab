from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "authorization-server",
        "role": "authorization_server",
    }


def test_unknown_resource() -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404