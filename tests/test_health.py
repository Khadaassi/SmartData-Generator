from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


def test_health_returns_ok_status():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "smartdata-generator"
    assert body["environment"] == "local"


def test_openapi_schema_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "SmartData Generator"


def test_docs_are_available():
    response = client.get("/docs")

    assert response.status_code == 200
