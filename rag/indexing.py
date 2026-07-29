from pathlib import Path

from rag.ingestion import ingest_corpus
from rag.vectorstore import upsert_chunks


def index_corpus(corpus_dir: Path, project_id: str) -> int:
    """Ingère et indexe l'ensemble des documents d'un corpus pour un projet donné.

    Retourne le nombre de chunks indexés.
    """
    chunks = ingest_corpus(corpus_dir, project_id)
    return upsert_chunks(chunks)
