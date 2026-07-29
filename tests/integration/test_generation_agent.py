import pytest

from agents.generation_agent import run_generation
from domain.generation import GenerationRequest
from domain.rules import BusinessRule
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


def _commande_rules() -> list[BusinessRule]:
    # Version structurée et déterministe des règles de rag/corpus/examples/regles_commande.md.
    return [
        BusinessRule(
            id="montant-positif",
            name="Montant total positif",
            type="range",
            field="montant_total",
            min_value=0,
            exclusive_min=True,
        ),
        BusinessRule(
            id="statut-valide",
            name="Statut de commande",
            type="allowed_values",
            field="statut",
            allowed_values=sorted(_ALLOWED_STATUSES),
        ),
        BusinessRule(id="reference-unique", name="Unicité de la référence", type="unique", field="reference"),
    ]


def test_agent_generates_data_respecting_business_rules(indexed_project_id):
    request = GenerationRequest(
        project_id=indexed_project_id, entity=_commande_entity(), count=3, rules=_commande_rules()
    )

    result = run_generation(request)

    assert result.status == "SUCCESS"
    assert len(result.items) == 3
    assert result.rules_used  # le RAG a bien retrouvé des règles métier pour l'entité Commande

    # Double contrôle : le LLM respecte les règles (guidées par le RAG), *et* le moteur
    # de validation déterministe le confirme indépendamment.
    assert result.validation_report is not None
    assert result.validation_report.status in ("PASSED", "PASSED_WITH_WARNINGS")
    assert result.validation_report.rejected_items == 0

    for item in result.items:
        assert item["montant_total"] > 0  # cf. regles_commande.md : "Montant total positif"
        assert item["statut"] in _ALLOWED_STATUSES  # cf. regles_commande.md : "Statut de commande"


def test_validation_engine_rejects_llm_output_that_violates_a_deterministic_rule(indexed_project_id):
    # Règle volontairement impossible à respecter : prouve que la validation rejette
    # bien des données produites par un vrai appel LLM, même sans erreur du modèle.
    impossible_rule = BusinessRule(
        id="montant-plafonne-a-zero",
        name="Montant plafonné à 0 (test)",
        type="range",
        field="montant_total",
        max_value=0,
    )
    request = GenerationRequest(
        project_id=indexed_project_id, entity=_commande_entity(), count=2, rules=[impossible_rule]
    )

    result = run_generation(request)

    assert result.validation_report is not None
    assert result.validation_report.status == "FAILED"
    assert result.items == []
    assert any(error.stage == "validation" for error in result.errors)


def test_agent_still_generates_data_when_no_business_rules_are_indexed():
    request = GenerationRequest(project_id="projet-sans-documentation", entity=_commande_entity(), count=1)

    result = run_generation(request)

    assert result.status == "SUCCESS"
    assert result.rules_used == []
    assert len(result.items) == 1
