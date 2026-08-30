from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_profile():
    response = client.get("/api/profile")

    assert response.status_code == 200
    assert response.json() == {
        "id": "demo-user",
        "display_name": "Lab User",
        "resource": "protected",
    }


def test_unknown_resource():
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404