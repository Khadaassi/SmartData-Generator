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
