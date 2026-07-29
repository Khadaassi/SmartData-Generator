from functools import lru_cache

from langchain_groq import ChatGroq

from infrastructure.config import get_settings


@lru_cache
def get_llm() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(model=settings.llm_model, api_key=settings.llm_api_key)
