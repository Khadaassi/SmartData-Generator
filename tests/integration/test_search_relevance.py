import time

import pytest

from rag.vectorstore import search
from tests.integration.conftest import rag_stack_reachable

pytestmark = pytest.mark.skipif(
    not rag_stack_reachable(),
    reason=(
        "Chroma (docker compose -f docker/docker-compose.yml up -d) "
        "ou Ollama (embeddings_base_url) non accessibles"
    ),
)


@pytest.mark.parametrize(
    ("query", "expected_entity", "expected_keyword"),
    [
        ("un client professionnel doit-il fournir un numéro d'entreprise ?", "Client", "professionnel"),
        ("le montant d'une commande peut-il être négatif ?", "Commande", "positif"),
        ("un motif est-il obligatoire en cas d'annulation d'une commande ?", "Commande", "annulation"),
        ("deux clients peuvent-ils partager la même adresse email ?", "Client", "email"),
    ],
)
def test_search_returns_relevant_top_result(indexed_project_id, query, expected_entity, expected_keyword):
    results = search(query, project_id=indexed_project_id, k=1)

    assert results
    top = results[0]
    assert top.metadata.entity == expected_entity
    assert expected_keyword in top.text.lower()


def test_search_ranks_relevant_results_above_less_relevant_ones(indexed_project_id):
    results = search("règles applicables à l'annulation d'une commande", project_id=indexed_project_id, k=6)

    assert len(results) > 1
    assert results[0].distance <= results[-1].distance


def test_search_is_scoped_to_the_requested_project(indexed_project_id):
    results = search("règles de gestion", project_id="un-projet-qui-nexiste-pas", k=5)

    assert results == []


def test_search_completes_within_a_reasonable_time(indexed_project_id):
    start = time.perf_counter()
    results = search("montant total d'une commande", project_id=indexed_project_id, k=3)
    elapsed = time.perf_counter() - start

    assert results
    assert elapsed < 5
