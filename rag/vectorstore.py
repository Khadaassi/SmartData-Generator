from functools import lru_cache

import chromadb
from chromadb.api.models.Collection import Collection

from infrastructure.config import get_settings
from infrastructure.embeddings import get_embeddings


@lru_cache
def get_chroma_client() -> chromadb.ClientAPI:
    settings = get_settings()
    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def get_collection() -> Collection:
    settings = get_settings()
    return get_chroma_client().get_or_create_collection(settings.chroma_collection_name)


def add_texts(texts: list[str], ids: list[str], metadatas: list[dict] | None = None) -> None:
    embeddings = get_embeddings().embed_documents(texts)
    get_collection().add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)


def similarity_search(query: str, k: int = 5) -> list[str]:
    query_embedding = get_embeddings().embed_query(query)
    results = get_collection().query(query_embeddings=[query_embedding], n_results=k)
    return results["documents"][0] if results["documents"] else []
