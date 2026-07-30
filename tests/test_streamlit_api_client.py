import httpx
import pytest

from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError


def _client(handler) -> ApiClient:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport, base_url="http://testserver")
    return ApiClient(client=http_client)


def test_check_health_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/health"
        return httpx.Response(200, json={"status": "ok", "service": "smartdata-generator", "version": "0.1.0", "environment": "local"})

    client = _client(handler)
    health = client.check_health()

    assert health["status"] == "ok"


def test_check_health_connection_error_raises_readable_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = _client(handler)

    with pytest.raises(SmartDataGeneratorApiError) as exc_info:
        client.check_health()

    assert exc_info.value.code == "connection_error"
    assert "Vérifiez qu'elle est démarrée" in exc_info.value.message


def test_check_health_timeout_raises_readable_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    client = _client(handler)

    with pytest.raises(SmartDataGeneratorApiError) as exc_info:
        client.check_health()

    assert exc_info.value.code == "timeout"


def test_analyze_postgres_schema_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/schema/postgres"
        return httpx.Response(
            200,
            json={
                "schema_name": "public",
                "tables": [{"name": "clients", "columns": [], "primary_key": [], "foreign_keys": [], "unique_constraints": [], "check_constraints": []}],
                "generation_order": ["clients"],
            },
        )

    client = _client(handler)
    result = client.analyze_postgres_schema({"database_url": "postgresql+psycopg://u:p@localhost/db"})

    assert result["schema_name"] == "public"
    assert result["generation_order"] == ["clients"]


def test_analyze_postgres_schema_502_raises_readable_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, json={"code": "connection_error", "message": "connexion refusée"})

    client = _client(handler)

    with pytest.raises(SmartDataGeneratorApiError) as exc_info:
        client.analyze_postgres_schema({"database_url": "postgresql+psycopg://u:p@localhost/db"})

    assert exc_info.value.status_code == 502
    assert exc_info.value.message == "connexion refusée"


def test_execute_generation_preview_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/executions"
        return httpx.Response(
            200,
            json={
                "run_id": "run-1",
                "mode": "PREVIEW",
                "status": "READY",
                "generation": {
                    "run_id": "run-1",
                    "status": "SUCCESS",
                    "entity": "Produit",
                    "items": [{"nom": "Clavier"}],
                    "rules_used": [],
                    "errors": [],
                    "validation_report": None,
                },
                "export_path": None,
                "insert_report": None,
            },
        )

    client = _client(handler)
    result = client.execute_generation(
        {"generation": {"project_id": "proj-1", "entity": {"name": "Produit", "fields": []}, "count": 1}, "mode": "PREVIEW"}
    )

    assert result["status"] == "READY"
    assert result["generation"]["items"] == [{"nom": "Clavier"}]


def test_execute_generation_insert_without_confirmation_passes_through_failed_status():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "run_id": "run-2",
                "mode": "INSERT",
                "status": "FAILED",
                "generation": {
                    "run_id": "run-2",
                    "status": "SUCCESS",
                    "entity": "Produit",
                    "items": [{"nom": "Clavier"}],
                    "rules_used": [],
                    "errors": [{"code": "insert_not_confirmed", "message": "confirmation requise", "stage": "insert", "blocking": True}],
                    "validation_report": None,
                },
                "export_path": None,
                "insert_report": None,
            },
        )

    client = _client(handler)
    result = client.execute_generation(
        {
            "generation": {"project_id": "proj-1", "entity": {"name": "Produit", "fields": []}, "count": 1},
            "mode": "INSERT",
            "confirm_insert": False,
        }
    )

    assert result["status"] == "FAILED"
    assert result["generation"]["errors"][0]["code"] == "insert_not_confirmed"


def test_create_project_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/projects"
        assert request.method == "POST"
        return httpx.Response(201, json={"id": "proj-1", "name": "Pricing", "description": None, "is_active": True})

    client = _client(handler)
    project = client.create_project({"name": "Pricing"})

    assert project["id"] == "proj-1"


def test_list_projects_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/projects"
        return httpx.Response(200, json=[{"id": "proj-1", "name": "Pricing"}])

    client = _client(handler)
    projects = client.list_projects()

    assert projects == [{"id": "proj-1", "name": "Pricing"}]


def test_get_project_404_raises_readable_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"code": "project_not_found", "message": "Projet introuvable : proj-1"})

    client = _client(handler)

    with pytest.raises(SmartDataGeneratorApiError) as exc_info:
        client.get_project("proj-1")

    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Projet introuvable : proj-1"


def test_update_project_rules_sends_rules_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/projects/proj-1/rules"
        assert request.method == "PUT"
        return httpx.Response(200, json={"id": "proj-1", "config": {"rules": [{"id": "r1"}]}})

    client = _client(handler)
    project = client.update_project_rules("proj-1", [{"id": "r1"}])

    assert project["config"]["rules"] == [{"id": "r1"}]


def test_upload_documents_sends_multipart_request():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/projects/proj-1/documents"
        assert request.headers["content-type"].startswith("multipart/form-data")
        assert b"filename=\"regles.md\"" in request.content
        assert b"contenu de test" in request.content
        return httpx.Response(200, json={"uploaded": [{"filename": "regles.md", "chunks_indexed": 1}]})

    client = _client(handler)
    result = client.upload_documents("proj-1", [("regles.md", b"contenu de test")])

    assert result["uploaded"][0]["chunks_indexed"] == 1


def test_list_documents_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/projects/proj-1/documents"
        return httpx.Response(200, json={"documents": ["regles_client"]})

    client = _client(handler)
    result = client.list_documents("proj-1")

    assert result == {"documents": ["regles_client"]}


def test_import_data_sends_multipart_request_with_confirmation():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/data-import/csv"
        assert request.headers["content-type"].startswith("multipart/form-data")
        assert b'name="confirm"' in request.content
        assert b"true" in request.content
        assert b'filename="produits.csv"' in request.content
        return httpx.Response(200, json={"table": "produits", "schema_name": "public", "rows_read": 2, "rows_inserted": 2})

    client = _client(handler)
    result = client.import_data(
        source_format="csv",
        filename="produits.csv",
        content=b"nom\nClavier\nSouris\n",
        database_url="postgresql+psycopg://u:p@localhost/db",
        schema_name="public",
        table="produits",
        confirm=True,
    )

    assert result["rows_inserted"] == 2


def test_import_data_400_raises_readable_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"code": "empty_file", "message": "Fichier CSV vide"})

    client = _client(handler)

    with pytest.raises(SmartDataGeneratorApiError) as exc_info:
        client.import_data(
            source_format="csv",
            filename="empty.csv",
            content=b"",
            database_url="postgresql+psycopg://u:p@localhost/db",
            schema_name="public",
            table="produits",
            confirm=True,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.message == "Fichier CSV vide"


def test_import_rest_data_sends_source_and_confirmation():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/data-import/rest"
        import json as _json

        captured["body"] = _json.loads(request.content)
        return httpx.Response(200, json={"table": "meteo", "schema_name": "public", "rows_read": 1, "rows_inserted": 1})

    client = _client(handler)
    result = client.import_rest_data(
        source={"url": "https://api.exemple.com/villes", "data_path": "data.items"},
        database_url="postgresql+psycopg://u:p@localhost/db",
        schema_name="public",
        table="meteo",
        confirm=True,
    )

    assert result["rows_inserted"] == 1
    assert captured["body"]["source"]["url"] == "https://api.exemple.com/villes"
    assert captured["body"]["confirm"] is True
    assert captured["body"]["table"] == "meteo"


def test_import_rest_data_422_raises_readable_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "L'import nécessite une confirmation explicite (confirm=true)."})

    client = _client(handler)

    with pytest.raises(SmartDataGeneratorApiError) as exc_info:
        client.import_rest_data(
            source={"url": "https://api.exemple.com/villes"},
            database_url="postgresql+psycopg://u:p@localhost/db",
            schema_name="public",
            table="meteo",
            confirm=False,
        )

    assert exc_info.value.status_code == 422


def test_delete_document_handles_empty_204_body():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/projects/proj-1/documents/regles_client.md"
        assert request.method == "DELETE"
        return httpx.Response(204)

    client = _client(handler)

    client.delete_document("proj-1", "regles_client.md")  # ne lève pas
