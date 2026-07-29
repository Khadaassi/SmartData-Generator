from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StreamlitSettings(BaseSettings):
    """Configuration de l'interface Streamlit : uniquement l'URL de l'API SmartData
    Generator et des paramètres d'affichage. Aucun secret Groq, PostgreSQL ou Ollama
    n'est chargé ici : Streamlit ne dépend que du contrat HTTP de l'API."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_base_url: str = Field(default="http://localhost:8000", alias="STREAMLIT_API_BASE_URL")
    request_timeout: float = Field(default=120.0, alias="STREAMLIT_REQUEST_TIMEOUT")
    application_title: str = Field(default="SmartData Generator", alias="STREAMLIT_APP_TITLE")
    environment: str = Field(default="local", alias="STREAMLIT_ENVIRONMENT")


@lru_cache
def get_settings() -> StreamlitSettings:
    return StreamlitSettings()
