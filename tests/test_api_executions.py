import pytest
from fastapi.testclient import TestClient

from api.app import app
from domain.generation import GenerationResult
from domain.project import ProjectConfig
from domain.rules import BusinessRule

client = TestClient(app)


@pytest.fixture(autouse=True)
def _default_project_rules(monkeypatch):
    # La plupart de ces tests portent sur le comportement de /executions par mode, pas sur
    # les règles d'un projet réel (cf. test_create_execution_applies_the_project_rules... plus
    # bas, qui override explicitement ce fixture).
    monkeypatch.setattr("application.execution_service.load_project_config", lambda project_id: ProjectConfig())


def _entity_payload() -> dict:
    return {"name": "Produit", "fields": [{"name": "nom", "type": "string"}]}


def _generation_result(**overrides) -> GenerationResult:
    data = {
        "run_id": "run-1",
        "status": "SUCCESS",
        "entity": "Produit",
        "items": [{"nom": "Clavier"}],
        "rules_used": [],
        "errors": [],
        "validation_report": None,
    }
    data.update(overrides)
    return GenerationResult(**data)


def test_create_execution_preview_mode_returns_ready(monkeypatch):
    monkeypatch.setattr("application.execution_service.run_generation", lambda request: _generation_result())

    response = client.post(
        "/executions",
        json={"generation": {"project_id": "proj-1", "entity": _entity_payload(), "count": 1}, "mode": "PREVIEW"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "READY"
    assert body["generation"]["items"] == [{"nom": "Clavier"}]
    assert body["export_path"] is None
    assert body["insert_report"] is None


def test_create_execution_defaults_to_preview_mode(monkeypatch):
    monkeypatch.setattr("application.execution_service.run_generation", lambda request: _generation_result())

    response = client.post(
        "/executions", json={"generation": {"project_id": "proj-1", "entity": _entity_payload(), "count": 1}}
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "PREVIEW"


def test_create_execution_insert_without_confirmation_returns_200_with_failed_status(monkeypatch):
    monkeypatch.setattr("application.execution_service.run_generation", lambda request: _generation_result())

    response = client.post(
        "/executions",
        json={
            "generation": {"project_id": "proj-1", "entity": _entity_payload(), "count": 1},
            "mode": "INSERT",
            "insert_target": {"database_url": "postgresql+psycopg://u:p@localhost/db", "table": "produits"},
            "confirm_insert": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FAILED"
    assert any(error["code"] == "insert_not_confirmed" for error in body["generation"]["errors"])


def test_create_execution_missing_generation_returns_422():
    response = client.post("/executions", json={"mode": "PREVIEW"})

    assert response.status_code == 422


def test_create_execution_applies_the_project_rules_regardless_of_the_request_body(monkeypatch):
    project_rules = [BusinessRule(id="prix-positif", name="Prix positif", type="range", field="prix", min_value=0)]
    monkeypatch.setattr(
        "application.execution_service.load_project_config",
        lambda project_id: ProjectConfig(rules=project_rules),
    )

    captured = {}

    def _fake_run_generation(request):
        captured["request"] = request
        return _generation_result()

    monkeypatch.setattr("application.execution_service.run_generation", _fake_run_generation)

    response = client.post(
        "/executions",
        json={"generation": {"project_id": "proj-1", "entity": _entity_payload(), "count": 1, "rules": []}},
    )

    assert response.status_code == 200
    assert captured["request"].rules == project_rules


def test_create_execution_invalid_mode_returns_422():
    response = client.post(
        "/executions",
        json={"generation": {"project_id": "proj-1", "entity": _entity_payload(), "count": 1}, "mode": "DESTROY"},
    )

    assert response.status_code == 422
