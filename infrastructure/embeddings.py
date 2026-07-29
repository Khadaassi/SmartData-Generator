from functools import lru_cache

from langchain_ollama import OllamaEmbeddings

from infrastructure.config import get_settings


@lru_cache
def get_embeddings() -> OllamaEmbeddings:
    settings = get_settings()
    return OllamaEmbeddings(model=settings.embeddings_model, base_url=settings.embeddings_base_url)
