import time
from uuid import uuid4

import pytest

from rag.indexing import index_corpus
from rag.vectorstore import get_collection
from tests.integration.conftest import EXAMPLES_DIR, rag_stack_reachable

pytestmark = pytest.mark.skipif(
    not rag_stack_reachable(),
    reason=(
        "Chroma (docker compose -f docker/docker-compose.yml up -d) "
        "ou Ollama (embeddings_base_url) non accessibles"
    ),
)


def _count_for_project(project_id: str) -> int:
    result = get_collection().get(where={"project_id": project_id})
    return len(result["ids"])


def test_index_corpus_indexes_every_chunk(indexed_project_id):
    count = _count_for_project(indexed_project_id)

    assert count > 0


def test_reindexing_is_idempotent(indexed_project_id):
    before = _count_for_project(indexed_project_id)

    index_corpus(EXAMPLES_DIR, indexed_project_id)

    after = _count_for_project(indexed_project_id)
    assert after == before


def test_indexing_completes_within_a_reasonable_time():
    project_id = f"test-rag-perf-{uuid4().hex}"

    start = time.perf_counter()
    count = index_corpus(EXAMPLES_DIR, project_id)
    elapsed = time.perf_counter() - start

    assert count > 0
    # Corpus d'exemple restreint, embeddings Ollama en local : large marge pour rester stable en CI/local.
    assert elapsed < 30
