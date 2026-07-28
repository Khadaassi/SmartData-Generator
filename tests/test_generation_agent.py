import pytest
from pydantic import ValidationError

from agents.generation_agent import (
    GenerationState,
    _generate_data,
    _retrieve_context,
    run_generation,
)
from domain.generation import GenerationRequest
from domain.schema import EntitySpec, FieldSpec, build_entity_model
from rag.schemas import ChunkMetadata
from rag.vectorstore import SearchResult


def _make_request(count: int = 2) -> GenerationRequest:
    entity = EntitySpec(
        name="Produit",
        fields=[
            FieldSpec(name="nom", type="string"),
            FieldSpec(name="prix", type="float"),
        ],
    )
    return GenerationRequest(project_id="test-project", entity=entity, count=count)


def _initial_state(request: GenerationRequest) -> GenerationState:
    return {
        "run_id": "test-run",
        "request": request,
        "context": [],
        "items": [],
        "errors": [],
        "status": "PENDING",
    }


class _FakeStructuredLLM:
    def __init__(self, model, items_data):
        self._model = model
        self._items_data = items_data

    def invoke(self, prompt):
        return self._model(items=self._items_data)


class _FakeLLM:
    def __init__(self, items_data):
        self._items_data = items_data

    def with_structured_output(self, model):
        return _FakeStructuredLLM(model, self._items_data)


class _FailingStructuredLLM:
    def invoke(self, prompt):
        raise RuntimeError("groq indisponible")


class _FailingLLM:
    def with_structured_output(self, model):
        return _FailingStructuredLLM()


def test_build_entity_model_creates_valid_pydantic_model():
    entity = EntitySpec(
        name="Client",
        fields=[
            FieldSpec(name="nom", type="string"),
            FieldSpec(name="age", type="integer", required=False),
        ],
    )
    model = build_entity_model(entity)

    instance = model(nom="Ada")
    assert instance.nom == "Ada"
    assert instance.age is None

    with pytest.raises(ValidationError):
        model()  # champ "nom" obligatoire manquant


def test_retrieve_context_node_handles_rag_failure(monkeypatch):
    def _raise(*args, **kwargs):
        raise RuntimeError("chroma indisponible")

    monkeypatch.setattr("agents.generation_agent.search", _raise)

    state = _retrieve_context(_initial_state(_make_request()))

    assert state["context"] == []
    assert len(state["errors"]) == 1
    assert state["errors"][0].code == "rag_unavailable"
    assert state["errors"][0].blocking is False


def test_generate_data_node_handles_llm_failure(monkeypatch):
    monkeypatch.setattr("agents.generation_agent.get_llm", lambda: _FailingLLM())

    state = _generate_data(_initial_state(_make_request()))

    assert state["status"] == "FAILED"
    assert state["items"] == []
    assert state["errors"][-1].code == "llm_generation_failed"
    assert state["errors"][-1].blocking is True


def test_generate_data_node_produces_structured_items(monkeypatch):
    items_data = [{"nom": "Clavier", "prix": 29.9}, {"nom": "Souris", "prix": 15.0}]
    monkeypatch.setattr("agents.generation_agent.get_llm", lambda: _FakeLLM(items_data))

    state = _generate_data(_initial_state(_make_request(count=2)))

    assert state["status"] == "SUCCESS"
    assert state["items"] == items_data
    assert state["errors"] == []


def test_generate_data_node_reports_incomplete_generation_as_non_blocking(monkeypatch):
    items_data = [{"nom": "Clavier", "prix": 29.9}]  # 1 seul objet alors que count=2
    monkeypatch.setattr("agents.generation_agent.get_llm", lambda: _FakeLLM(items_data))

    state = _generate_data(_initial_state(_make_request(count=2)))

    assert state["status"] == "SUCCESS"
    assert len(state["items"]) == 1
    assert state["errors"][0].code == "incomplete_generation"
    assert state["errors"][0].blocking is False


def test_run_generation_end_to_end_with_fakes(monkeypatch):
    fake_context = [
        SearchResult(
            text="Le prix doit toujours être positif.",
            metadata=ChunkMetadata(
                document_id="doc",
                project_id="test-project",
                source_filename="doc.md",
                title="Règles produit",
                category="rule",
                entity="Produit",
                chunk_index=0,
                section="Prix",
            ),
            distance=0.1,
        )
    ]
    monkeypatch.setattr("agents.generation_agent.search", lambda *a, **k: fake_context)
    items_data = [{"nom": "Clavier", "prix": 29.9}, {"nom": "Souris", "prix": 15.0}]
    monkeypatch.setattr("agents.generation_agent.get_llm", lambda: _FakeLLM(items_data))

    result = run_generation(_make_request(count=2))

    assert result.status == "SUCCESS"
    assert result.items == items_data
    assert result.rules_used == ["Le prix doit toujours être positif."]
    assert result.errors == []
