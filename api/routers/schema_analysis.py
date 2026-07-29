from fastapi import APIRouter

from api.schemas.errors import ErrorResponse
from api.schemas.schema_analysis import PostgresSchemaRequest
from connectors.postgres import DatabaseSchema, read_schema

router = APIRouter(prefix="/schema", tags=["schema"])


@router.post(
    "/postgres",
    response_model=DatabaseSchema,
    summary="Analyser le schéma d'une base PostgreSQL",
    description=(
        "Inspecte une base PostgreSQL et retourne une représentation normalisée : tables, "
        "colonnes, clés primaires, clés étrangères, contraintes, et un ordre de génération "
        "respectant les dépendances entre tables."
    ),
    responses={502: {"model": ErrorResponse, "description": "Connexion impossible ou schéma introuvable"}},
)
def analyze_postgres_schema(request: PostgresSchemaRequest) -> DatabaseSchema:
    return read_schema(request.database_url, schema=request.schema_name)
