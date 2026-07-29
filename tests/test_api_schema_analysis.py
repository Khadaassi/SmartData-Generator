from fastapi.testclient import TestClient

from api.app import app
from connectors.postgres import (
    ColumnSchema,
    DatabaseSchema,
    SchemaReaderError,
    TableSchema,
)

client = TestClient(app)


def _fake_schema() -> DatabaseSchema:
    return DatabaseSchema(
        schema_name="public",
        tables=[
            TableSchema(
                name="clients",
                columns=[ColumnSchema(name="id", data_type="integer", nullable=False, is_primary_key=True)],
                primary_key=["id"],
            )
        ],
        generation_order=["clients"],
    )


def test_analyze_postgres_schema_returns_normalized_schema(monkeypatch):
    monkeypatch.setattr("api.routers.schema_analysis.read_schema", lambda database_url, schema: _fake_schema())

    response = client.post("/schema/postgres", json={"database_url": "postgresql+psycopg://u:p@localhost/db"})

    assert response.status_code == 200
    body = response.json()
    assert body["schema_name"] == "public"
    assert body["tables"][0]["name"] == "clients"
    assert body["generation_order"] == ["clients"]


def test_analyze_postgres_schema_uses_default_schema_name(monkeypatch):
    captured = {}

    def _fake(database_url, schema):
        captured["schema"] = schema
        return _fake_schema()

    monkeypatch.setattr("api.routers.schema_analysis.read_schema", _fake)

    client.post("/schema/postgres", json={"database_url": "postgresql+psycopg://u:p@localhost/db"})

    assert captured["schema"] == "public"


def test_analyze_postgres_schema_connection_error_returns_502(monkeypatch):
    def _raise(database_url, schema):
        raise SchemaReaderError(code="connection_error", message="connexion refusée")

    monkeypatch.setattr("api.routers.schema_analysis.read_schema", _raise)

    response = client.post("/schema/postgres", json={"database_url": "postgresql+psycopg://u:p@localhost/db"})

    assert response.status_code == 502
    body = response.json()
    assert body["code"] == "connection_error"
    assert body["message"] == "connexion refusée"


def test_analyze_postgres_schema_unexpected_error_returns_500(monkeypatch):
    # Le handler de la classe Exception est câblé dans ServerErrorMiddleware, qui reconstruit
    # bien la réponse 500 pour un vrai client HTTP mais re-lève ensuite l'exception (pour les
    # logs serveur) : TestClient doit donc ne pas la propager pour observer la réponse produite.
    no_raise_client = TestClient(app, raise_server_exceptions=False)

    def _raise(database_url, schema):
        raise RuntimeError("panne inattendue")

    monkeypatch.setattr("api.routers.schema_analysis.read_schema", _raise)

    response = no_raise_client.post("/schema/postgres", json={"database_url": "postgresql+psycopg://u:p@localhost/db"})

    assert response.status_code == 500
    assert response.json()["code"] == "internal_error"


def test_analyze_postgres_schema_missing_database_url_returns_422():
    response = client.post("/schema/postgres", json={})

    assert response.status_code == 422
