from datetime import UTC, datetime

from fastapi.testclient import TestClient

from api.app import app
from domain.project import Project, ProjectConfig

client = TestClient(app)


def _project(**overrides) -> Project:
    now = datetime.now(UTC)
    data = {
        "id": "proj-1",
        "name": "Pricing",
        "description": None,
        "config": ProjectConfig(),
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return Project(**data)


def test_create_project_returns_created_project(monkeypatch):
    monkeypatch.setattr(
        "application.project_service.insert_project", lambda project: None
    )

    response = client.post("/projects", json={"name": "Pricing", "description": "Démo"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Pricing"
    assert body["description"] == "Démo"
    assert body["id"]


def test_list_projects_returns_all_projects(monkeypatch):
    projects = [_project(id="a"), _project(id="b")]
    monkeypatch.setattr(
        "application.project_service.list_all_projects", lambda active_only: projects if not active_only else []
    )

    response = client.get("/projects")

    assert response.status_code == 200
    assert [p["id"] for p in response.json()] == ["a", "b"]


def test_get_project_returns_the_project(monkeypatch):
    stored = _project()
    monkeypatch.setattr(
        "application.project_service.find_project", lambda project_id: stored if project_id == "proj-1" else None
    )

    response = client.get("/projects/proj-1")

    assert response.status_code == 200
    assert response.json()["id"] == "proj-1"


def test_get_project_returns_404_when_missing(monkeypatch):
    monkeypatch.setattr("application.project_service.find_project", lambda project_id: None)

    response = client.get("/projects/does-not-exist")

    assert response.status_code == 404
    assert response.json()["code"] == "project_not_found"


def test_replace_rules_updates_the_project_config(monkeypatch):
    stored = _project()
    captured = {}
    monkeypatch.setattr("application.project_service.find_project", lambda project_id: stored)
    monkeypatch.setattr(
        "application.project_service.update_project_row", lambda project: captured.setdefault("project", project)
    )

    rule = {"id": "r1", "name": "Prix positif", "type": "range", "field": "prix", "min_value": 0}
    response = client.put("/projects/proj-1/rules", json={"rules": [rule]})

    assert response.status_code == 200
    body = response.json()
    assert len(body["config"]["rules"]) == 1
    assert body["config"]["rules"][0]["field"] == "prix"


def test_delete_project_returns_204(monkeypatch):
    monkeypatch.setattr("application.project_service.delete_project_row", lambda project_id: True)

    response = client.delete("/projects/proj-1")

    assert response.status_code == 204


def test_delete_project_returns_404_when_missing(monkeypatch):
    monkeypatch.setattr("application.project_service.delete_project_row", lambda project_id: False)

    response = client.delete("/projects/does-not-exist")

    assert response.status_code == 404
