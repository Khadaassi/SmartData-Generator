from urllib.parse import urlparse
from uuid import uuid4

import pytest

from infrastructure.config import get_settings
from rag.vectorstore import add_texts, similarity_search
from tests.integration._reachability import is_reachable

settings = get_settings()
_ollama_url = urlparse(settings.embeddings_base_url)

pytestmark = pytest.mark.skipif(
    not is_reachable(settings.chroma_host, settings.chroma_port)
    or not is_reachable(_ollama_url.hostname, _ollama_url.port),
    reason=(
        "Chroma (docker compose -f docker/docker-compose.yml up -d) "
        "or Ollama (embeddings_base_url) not reachable"
    ),
)


def test_chroma_add_and_query_round_trip():
    rule_id = f"test-rule-{uuid4().hex}"
    add_texts(
        texts=["Une remise ne peut jamais dépasser 50 pourcent du prix."],
        ids=[rule_id],
    )

    results = similarity_search("quelle est la limite de remise autorisée ?", k=1)

    assert results
    assert "remise" in results[0]
