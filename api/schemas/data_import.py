from pydantic import BaseModel


class ImportResult(BaseModel):
    """Résultat d'un import direct de fichier (CSV/JSON) vers une table PostgreSQL."""

    table: str
    schema_name: str
    rows_read: int
    rows_inserted: int
