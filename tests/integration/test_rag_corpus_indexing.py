from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import pytest

import rag
from infrastructure.config import get_settings
from infrastructure.embeddings import get_embeddings
from rag.ingestion import ingest_corpus
from rag.vectorstore import get_chroma_client
from tests.integration._reachability import is_reachable

settings = get_settings()
_ollama_url = urlparse(settings.embeddings_base_url)
_EXAMPLES_DIR = Path(rag.__file__).resolve().parent / "corpus" / "examples"

pytestmark = pytest.mark.skipif(
    not is_reachable(settings.chroma_host, settings.chroma_port)
    or not is_reachable(_ollama_url.hostname, _ollama_url.port),
    reason=(
        "Chroma (docker compose -f docker/docker-compose.yml up -d) "
        "ou Ollama (embeddings_base_url) non accessibles"
    ),
)


def test_example_corpus_can_be_indexed_and_retrieved_with_metadata():
    project_id = f"test-corpus-{uuid4().hex}"
    chunks = ingest_corpus(_EXAMPLES_DIR, project_id=project_id)

    embeddings = get_embeddings()
    texts = [text for text, _ in chunks]
    vectors = embeddings.embed_documents(texts)
    ids = [f"{metadata.document_id}-{metadata.chunk_index}-{project_id}" for _, metadata in chunks]
    metadatas = [metadata.to_chroma_metadata() for _, metadata in chunks]

    collection = get_chroma_client().get_or_create_collection(settings.chroma_collection_name)
    collection.add(ids=ids, documents=texts, embeddings=vectors, metadatas=metadatas)

    query_embedding = embeddings.embed_query(
        "un client professionnel doit-il fournir un numéro d'entreprise ?"
    )
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1,
        where={"project_id": project_id},
    )

    assert results["documents"][0]
    assert "professionnel" in results["documents"][0][0].lower()
    assert results["metadatas"][0][0]["entity"] == "Client"
