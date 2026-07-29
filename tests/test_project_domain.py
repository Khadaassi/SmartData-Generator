from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from domain.project import ConnectorConfig, GenerationParameters, Project, ProjectConfig
from domain.schema import EntitySpec, FieldSpec


def test_generation_parameters_defaults():
    params = GenerationParameters()

    assert params.default_count == 10
    assert params.llm_provider is None


def test_project_config_defaults_to_empty():
    config = ProjectConfig()

    assert config.entities == []
    assert config.rules == []
    assert config.source is None
    assert config.destination is None


def test_project_config_rejects_duplicate_entity_names():
    entities = [
        EntitySpec(name="Client", fields=[FieldSpec(name="nom", type="string")]),
        EntitySpec(name="Client", fields=[FieldSpec(name="email", type="string")]),
    ]

    with pytest.raises(ValidationError, match="doublon"):
        ProjectConfig(entities=entities)


def test_project_config_accepts_distinct_entity_names():
    entities = [
        EntitySpec(name="Client", fields=[FieldSpec(name="nom", type="string")]),
        EntitySpec(name="Commande", fields=[FieldSpec(name="montant", type="float")]),
    ]

    config = ProjectConfig(entities=entities)

    assert [entity.name for entity in config.entities] == ["Client", "Commande"]


def test_connector_config_accepts_arbitrary_type_specific_config():
    connector = ConnectorConfig(type="postgres", config={"database_url": "postgresql+psycopg://u:p@host/db"})

    assert connector.type == "postgres"
    assert connector.config["database_url"] == "postgresql+psycopg://u:p@host/db"


def test_project_requires_a_non_empty_name():
    with pytest.raises(ValidationError):
        Project(id="p1", name="", created_at=datetime.now(UTC), updated_at=datetime.now(UTC))
