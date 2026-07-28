import tomllib
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str = "postgresql+psycopg://smartdata:smartdata@localhost:5432/smartdata_generator"

    chroma_host: str = "localhost"
    chroma_port: int = 8020
    chroma_collection_name: str = "smartdata_generator"

    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_api_key: str = ""

    embeddings_provider: str = "ollama"
    embeddings_model: str = "mxbai-embed-large"
    embeddings_base_url: str = "http://localhost:11434"

    documents_storage_dir: str = "./data/documents"
    export_output_dir: str = "./data/exports"


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_project_version() -> str:
    with _PYPROJECT_PATH.open("rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]
