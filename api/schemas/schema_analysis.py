from pydantic import BaseModel


class PostgresSchemaRequest(BaseModel):
    """Requête d'analyse de schéma PostgreSQL.

    Rien n'est supposé par défaut : la base et le schéma cibles doivent être
    fournis explicitement (cf. technical_architecture.md section 6.25)."""

    database_url: str
    schema_name: str = "public"
