from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_authorization_server_health() -> None:
    response = client.get("/oauth/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "authorization-server",
        "role": "authorization_server",
    }


def test_resource_server_health() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_resource_profile() -> None:
    response = client.get("/api/profile")

    assert response.status_code == 200
    assert response.json() == {
        "id": "demo-user",
        "display_name": "Lab User",
        "resource": "protected",
    }


def test_unknown_resource() -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404