import pytest

from agents.generation_agent import run_generation
from domain.generation import GenerationRequest
from domain.schema import EntitySpec, FieldSpec
from infrastructure.config import get_settings
from tests.integration.conftest import rag_stack_reachable

settings = get_settings()

pytestmark = pytest.mark.skipif(
    not rag_stack_reachable() or not settings.llm_api_key,
    reason=(
        "Stack RAG (Chroma/Ollama, docker compose -f docker/docker-compose.yml up -d) "
        "et/ou clé Groq (LLM_API_KEY) non disponibles"
    ),
)

_ALLOWED_STATUSES = {"EN_ATTENTE", "CONFIRMEE", "EXPEDIEE", "LIVREE", "ANNULEE"}


def _commande_entity() -> EntitySpec:
    return EntitySpec(
        name="Commande",
        fields=[
            FieldSpec(name="reference", type="string", description="Référence unique de la commande"),
            FieldSpec(name="client_id", type="string"),
            FieldSpec(name="montant_total", type="float", description="Montant total de la commande"),
            FieldSpec(name="statut", type="string", allowed_values=sorted(_ALLOWED_STATUSES)),
            FieldSpec(name="date_commande", type="date"),
        ],
    )


def test_agent_generates_data_respecting_business_rules(indexed_project_id):
    request = GenerationRequest(project_id=indexed_project_id, entity=_commande_entity(), count=3)

    result = run_generation(request)

    assert result.status == "SUCCESS"
    assert len(result.items) == 3
    assert result.rules_used  # le RAG a bien retrouvé des règles métier pour l'entité Commande

    for item in result.items:
        assert item["montant_total"] > 0  # cf. regles_commande.md : "Montant total positif"
        assert item["statut"] in _ALLOWED_STATUSES  # cf. regles_commande.md : "Statut de commande"


def test_agent_still_generates_data_when_no_business_rules_are_indexed():
    request = GenerationRequest(project_id="projet-sans-documentation", entity=_commande_entity(), count=1)

    result = run_generation(request)

    assert result.status == "SUCCESS"
    assert result.rules_used == []
    assert len(result.items) == 1
