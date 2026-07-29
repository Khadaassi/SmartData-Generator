from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import pytest

import rag
from infrastructure.config import get_settings
from rag.indexing import index_corpus
from tests.integration._reachability import is_reachable

settings = get_settings()
_ollama_url = urlparse(settings.embeddings_base_url)

EXAMPLES_DIR = Path(rag.__file__).resolve().parent / "corpus" / "examples"


def rag_stack_reachable() -> bool:
    return is_reachable(settings.chroma_host, settings.chroma_port) and is_reachable(
        _ollama_url.hostname, _ollama_url.port
    )


@pytest.fixture(scope="module")
def indexed_project_id() -> str:
    project_id = f"test-rag-{uuid4().hex}"
    index_corpus(EXAMPLES_DIR, project_id)
    return project_id
