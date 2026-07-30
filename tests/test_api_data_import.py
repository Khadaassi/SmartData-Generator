from fastapi.testclient import TestClient

from api.app import app
from connectors.input import DataReaderError
from connectors.postgres import DataWriteError

client = TestClient(app)


def _files(name: str = "clients.csv", content: bytes = b"nom,email\nAlice,alice@example.com\n"):
    return {"file": (name, content, "text/csv")}


def test_import_csv_inserts_records(monkeypatch):
    captured = {}

    def _fake_insert(database_url, *, schema, table, items):
        captured["database_url"] = database_url
        captured["schema"] = schema
        captured["table"] = table
        captured["items"] = items
        return len(items)

    monkeypatch.setattr("api.routers.data_import.insert_records", _fake_insert)

    response = client.post(
        "/data-import/csv",
        files=_files(),
        data={
            "database_url": "postgresql+psycopg://u:p@localhost/db",
            "schema_name": "public",
            "table": "clients",
            "confirm": "true",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {"table": "clients", "schema_name": "public", "rows_read": 1, "rows_inserted": 1}
    assert captured["items"] == [{"nom": "Alice", "email": "alice@example.com"}]
    assert captured["table"] == "clients"


def test_import_csv_without_confirmation_returns_422():
    response = client.post(
        "/data-import/csv",
        files=_files(),
        data={"database_url": "postgresql+psycopg://u:p@localhost/db", "table": "clients", "confirm": "false"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "L'import nécessite une confirmation explicite (confirm=true)."


def test_import_csv_missing_confirmation_defaults_to_false():
    response = client.post(
        "/data-import/csv",
        files=_files(),
        data={"database_url": "postgresql+psycopg://u:p@localhost/db", "table": "clients"},
    )

    assert response.status_code == 422


def test_import_csv_invalid_file_returns_400(monkeypatch):
    response = client.post(
        "/data-import/csv",
        files=_files(name="empty.csv", content=b""),
        data={"database_url": "postgresql+psycopg://u:p@localhost/db", "table": "clients", "confirm": "true"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "empty_file"


def test_import_csv_write_error_returns_502(monkeypatch):
    def _raise(database_url, *, schema, table, items):
        raise DataWriteError(code="connection_error", message="connexion refusée")

    monkeypatch.setattr("api.routers.data_import.insert_records", _raise)

    response = client.post(
        "/data-import/csv",
        files=_files(),
        data={"database_url": "postgresql+psycopg://u:p@localhost/db", "table": "clients", "confirm": "true"},
    )

    assert response.status_code == 502
    assert response.json()["code"] == "connection_error"


def test_import_json_inserts_records(monkeypatch):
    captured = {}

    def _fake_insert(database_url, *, schema, table, items):
        captured["items"] = items
        return len(items)

    monkeypatch.setattr("api.routers.data_import.insert_records", _fake_insert)

    response = client.post(
        "/data-import/json",
        files={"file": ("produits.json", b'[{"nom": "Clavier"}]', "application/json")},
        data={"database_url": "postgresql+psycopg://u:p@localhost/db", "table": "produits", "confirm": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["rows_read"] == 1
    assert body["rows_inserted"] == 1
    assert captured["items"] == [{"nom": "Clavier"}]


def test_import_json_invalid_syntax_returns_400():
    response = client.post(
        "/data-import/json",
        files={"file": ("invalid.json", b"{not valid json", "application/json")},
        data={"database_url": "postgresql+psycopg://u:p@localhost/db", "table": "produits", "confirm": "true"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "json_parse_error"
