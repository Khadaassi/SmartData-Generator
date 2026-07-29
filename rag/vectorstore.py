from dataclasses import dataclass
from functools import lru_cache

import chromadb
from chromadb.api.models.Collection import Collection

from infrastructure.config import get_settings
from infrastructure.embeddings import get_embeddings
from rag.schemas import ChunkMetadata


@lru_cache
def get_chroma_client() -> chromadb.ClientAPI:
    settings = get_settings()
    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def get_collection() -> Collection:
    settings = get_settings()
    return get_chroma_client().get_or_create_collection(settings.chroma_collection_name)


def _chunk_id(metadata: ChunkMetadata) -> str:
    return f"{metadata.project_id}:{metadata.document_id}:{metadata.chunk_index}"


def upsert_chunks(chunks: list[tuple[str, ChunkMetadata]]) -> int:
    """Génère les embeddings et indexe (ou met à jour) des chunks dans ChromaDB.

    Les identifiants sont déterministes (projet/document/index) : ré-indexer un
    corpus inchangé met simplement à jour les mêmes entrées au lieu de les dupliquer.
    """
    if not chunks:
        return 0

    texts = [text for text, _ in chunks]
    metadatas = [metadata for _, metadata in chunks]
    ids = [_chunk_id(metadata) for metadata in metadatas]
    embeddings = get_embeddings().embed_documents(texts)

    get_collection().upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=[metadata.to_chroma_metadata() for metadata in metadatas],
    )
    return len(ids)


def delete_document(project_id: str, document_id: str) -> None:
    """Supprime tous les chunks d'un document donné pour un projet."""
    get_collection().delete(where={"$and": [{"project_id": project_id}, {"document_id": document_id}]})


def list_documents(project_id: str) -> list[str]:
    """Liste les identifiants de document distincts indexés pour un projet."""
    result = get_collection().get(where={"project_id": project_id}, include=["metadatas"])
    return sorted({metadata["document_id"] for metadata in result["metadatas"]})


@dataclass
class SearchResult:
    text: str
    metadata: ChunkMetadata
    distance: float


def search(query: str, project_id: str, k: int = 5, entity: str | None = None) -> list[SearchResult]:
    """Recherche sémantique dans le corpus indexé d'un projet, filtrable par entité."""
    where = {"project_id": project_id} if entity is None else {"$and": [{"project_id": project_id}, {"entity": entity}]}

    query_embedding = get_embeddings().embed_query(query)
    results = get_collection().query(query_embeddings=[query_embedding], n_results=k, where=where)

    if not results["documents"] or not results["documents"][0]:
        return []

    return [
        SearchResult(text=text, metadata=ChunkMetadata.model_validate(metadata), distance=distance)
        for text, metadata, distance in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0], strict=True
        )
    ]
