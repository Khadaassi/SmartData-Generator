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

    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "smartdata_generator"

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str = ""

    embeddings_provider: str = "openai"
    embeddings_model: str = "text-embedding-3-small"
    embeddings_api_key: str = ""

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
