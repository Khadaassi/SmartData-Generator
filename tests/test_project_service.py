from datetime import UTC, datetime

import pytest

from application.project_service import (
    ProjectNotFoundError,
    create_project,
    delete_project,
    get_project,
    list_projects,
    load_project_config,
    set_project_active,
    update_project_config,
)
from domain.project import Project, ProjectConfig
from domain.schema import EntitySpec, FieldSpec


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


def test_create_project_persists_and_returns_it(monkeypatch):
    captured = {}
    monkeypatch.setattr("application.project_service.insert_project", lambda project: captured.setdefault("project", project))

    config = ProjectConfig(entities=[EntitySpec(name="Client", fields=[FieldSpec(name="nom", type="string")])])
    project = create_project("Pricing", description="Démonstrateur", config=config)

    assert project.name == "Pricing"
    assert project.description == "Démonstrateur"
    assert project.is_active is True
    assert project.id  # un id a été généré
    assert captured["project"] == project


def test_get_project_returns_stored_project(monkeypatch):
    stored = _project()
    monkeypatch.setattr("application.project_service.find_project", lambda project_id: stored if project_id == "proj-1" else None)

    assert get_project("proj-1") == stored


def test_get_project_raises_not_found_when_missing(monkeypatch):
    monkeypatch.setattr("application.project_service.find_project", lambda project_id: None)

    with pytest.raises(ProjectNotFoundError):
        get_project("does-not-exist")


def test_list_projects_delegates_to_repository(monkeypatch):
    projects = [_project(id="a"), _project(id="b")]
    monkeypatch.setattr("application.project_service.list_all_projects", lambda active_only: projects if not active_only else [])

    assert list_projects() == projects
    assert list_projects(active_only=True) == []


def test_load_project_config_returns_the_stored_config(monkeypatch):
    config = ProjectConfig(entities=[EntitySpec(name="Commande", fields=[FieldSpec(name="montant", type="float")])])
    stored = _project(config=config)
    monkeypatch.setattr("application.project_service.find_project", lambda project_id: stored)

    assert load_project_config("proj-1") == config


def test_update_project_config_persists_new_config_and_bumps_updated_at(monkeypatch):
    original = _project()
    monkeypatch.setattr("application.project_service.find_project", lambda project_id: original)
    captured = {}
    monkeypatch.setattr("application.project_service.update_project_row", lambda project: captured.setdefault("project", project))

    new_config = ProjectConfig(entities=[EntitySpec(name="Client", fields=[FieldSpec(name="nom", type="string")])])
    updated = update_project_config("proj-1", new_config)

    assert updated.config == new_config
    assert updated.updated_at >= original.updated_at
    assert captured["project"] == updated


def test_set_project_active_toggles_flag(monkeypatch):
    original = _project(is_active=True)
    monkeypatch.setattr("application.project_service.find_project", lambda project_id: original)
    monkeypatch.setattr("application.project_service.update_project_row", lambda project: None)

    deactivated = set_project_active("proj-1", False)

    assert deactivated.is_active is False


def test_delete_project_raises_not_found_when_nothing_was_deleted(monkeypatch):
    monkeypatch.setattr("application.project_service.delete_project_row", lambda project_id: False)

    with pytest.raises(ProjectNotFoundError):
        delete_project("does-not-exist")


def test_delete_project_succeeds_when_a_row_was_removed(monkeypatch):
    monkeypatch.setattr("application.project_service.delete_project_row", lambda project_id: True)

    delete_project("proj-1")  # ne lève pas
