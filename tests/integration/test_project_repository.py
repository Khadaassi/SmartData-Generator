import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from domain.project import ConnectorConfig, Project, ProjectConfig
from domain.schema import EntitySpec, FieldSpec
from infrastructure.config import get_settings
from persistence.project_repository import (
    delete_project_row,
    find_project,
    insert_project,
    list_all_projects,
    update_project_row,
)
from persistence.tables import create_all
from tests.integration._reachability import is_reachable

settings = get_settings()
_db_url = make_url(settings.database_url)

pytestmark = pytest.mark.skipif(
    not is_reachable(_db_url.host, _db_url.port or 5432),
    reason="PostgreSQL non accessible (docker compose -f docker/docker-compose.yml up -d postgres)",
)


@pytest.fixture(scope="module")
def engine():
    db_engine = create_engine(settings.database_url)
    create_all(db_engine)
    yield db_engine
    db_engine.dispose()


def _make_project(**overrides) -> Project:
    now = datetime.now(UTC)
    data = {
        "id": f"t15_{uuid.uuid4().hex[:8]}",
        "name": "Pricing Control Tower",
        "description": "Démonstrateur",
        "config": ProjectConfig(),
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    data.update(overrides)
    return Project(**data)


@pytest.fixture
def cleanup(engine):
    created_ids: list[str] = []
    yield created_ids
    for project_id in created_ids:
        delete_project_row(project_id, engine=engine)


def test_insert_and_find_project_round_trips(engine, cleanup):
    config = ProjectConfig(
        entities=[EntitySpec(name="Client", fields=[FieldSpec(name="nom", type="string")])],
        source=ConnectorConfig(type="postgres", config={"database_url": "postgresql+psycopg://u:p@host/db"}),
    )
    project = _make_project(config=config)
    cleanup.append(project.id)

    insert_project(project, engine=engine)
    found = find_project(project.id, engine=engine)

    assert found == project


def test_find_project_returns_none_when_missing(engine):
    assert find_project(f"does-not-exist-{uuid.uuid4().hex}", engine=engine) is None


def test_two_projects_have_independent_configurations(engine, cleanup):
    config_a = ProjectConfig(entities=[EntitySpec(name="Client", fields=[FieldSpec(name="nom", type="string")])])
    config_b = ProjectConfig(entities=[EntitySpec(name="Commande", fields=[FieldSpec(name="montant", type="float")])])
    project_a = _make_project(name="Projet A", config=config_a)
    project_b = _make_project(name="Projet B", config=config_b)
    cleanup.extend([project_a.id, project_b.id])

    insert_project(project_a, engine=engine)
    insert_project(project_b, engine=engine)

    found_a = find_project(project_a.id, engine=engine)
    found_b = find_project(project_b.id, engine=engine)

    assert found_a.config == config_a
    assert found_b.config == config_b
    assert found_a.config != found_b.config


def test_update_project_row_changes_only_the_targeted_project(engine, cleanup):
    project_a = _make_project(name="Projet A")
    project_b = _make_project(name="Projet B")
    cleanup.extend([project_a.id, project_b.id])
    insert_project(project_a, engine=engine)
    insert_project(project_b, engine=engine)

    new_config = ProjectConfig(entities=[EntitySpec(name="Produit", fields=[FieldSpec(name="nom", type="string")])])
    updated_a = project_a.model_copy(update={"config": new_config, "is_active": False})

    was_updated = update_project_row(updated_a, engine=engine)

    assert was_updated is True
    assert find_project(project_a.id, engine=engine).config == new_config
    assert find_project(project_a.id, engine=engine).is_active is False
    assert find_project(project_b.id, engine=engine).config == ProjectConfig()  # non affecté


def test_update_project_row_returns_false_for_unknown_project(engine):
    ghost = _make_project(id=f"does-not-exist-{uuid.uuid4().hex}")

    assert update_project_row(ghost, engine=engine) is False


def test_list_all_projects_filters_active_only(engine, cleanup):
    active = _make_project(name="Actif", is_active=True)
    inactive = _make_project(name="Inactif", is_active=False)
    cleanup.extend([active.id, inactive.id])
    insert_project(active, engine=engine)
    insert_project(inactive, engine=engine)

    all_ids = {project.id for project in list_all_projects(engine=engine)}
    active_ids = {project.id for project in list_all_projects(active_only=True, engine=engine)}

    assert {active.id, inactive.id} <= all_ids
    assert active.id in active_ids
    assert inactive.id not in active_ids


def test_delete_project_row_removes_it(engine):
    project = _make_project()
    insert_project(project, engine=engine)

    was_deleted = delete_project_row(project.id, engine=engine)

    assert was_deleted is True
    assert find_project(project.id, engine=engine) is None


def test_delete_project_row_returns_false_for_unknown_project(engine):
    assert delete_project_row(f"does-not-exist-{uuid.uuid4().hex}", engine=engine) is False
