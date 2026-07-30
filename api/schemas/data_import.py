from pydantic import BaseModel

from connectors.input.rest_client import RestSourceConfig


class ImportResult(BaseModel):
    """Résultat d'un import direct (fichier ou API REST) vers une table PostgreSQL."""

    table: str
    schema_name: str
    rows_read: int
    rows_inserted: int


class RestImportRequest(BaseModel):
    """Requête d'import direct depuis une API REST vers une table PostgreSQL.

    Rien n'est supposé par défaut (URL, méthode, authentification, chemin d'extraction) :
    tout provient de `source`, revalidé par le connecteur REST (cf. RestSourceConfig)."""

    source: RestSourceConfig
    database_url: str
    schema_name: str = "public"
    table: str
    confirm: bool = False
