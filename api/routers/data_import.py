import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.schemas.data_import import ImportResult, RestImportRequest
from api.schemas.errors import ErrorResponse
from connectors.input import read_csv, read_json, read_rest
from connectors.postgres import insert_records

router = APIRouter(prefix="/data-import", tags=["data-import"])

_CONFIRMATION_MESSAGE = "L'import nécessite une confirmation explicite (confirm=true)."
_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Fichier invalide (syntaxe, encodage, structure)"},
    422: {"model": ErrorResponse, "description": "Confirmation d'import absente"},
    502: {"model": ErrorResponse, "description": "Connexion PostgreSQL impossible ou insertion refusée"},
}


def _require_confirmation(confirm: bool) -> None:
    if not confirm:
        raise HTTPException(status_code=422, detail=_CONFIRMATION_MESSAGE)


def _insert(records: list[dict], *, database_url: str, schema_name: str, table: str) -> ImportResult:
    rows_inserted = insert_records(database_url, schema=schema_name, table=table, items=records)
    return ImportResult(table=table, schema_name=schema_name, rows_read=len(records), rows_inserted=rows_inserted)


@router.post(
    "/csv",
    response_model=ImportResult,
    summary="Importer un fichier CSV directement dans une table PostgreSQL",
    description=(
        "Lit un fichier CSV fourni par l'utilisateur et insère les enregistrements tels quels dans "
        "la table cible, sans passer par la génération LLM : destiné à charger des données déjà "
        "correctes (ex. catalogue produits issu d'un scraping). L'import n'est jamais implicite : "
        "il exige une confirmation explicite (confirm=true)."
    ),
    responses=_RESPONSES,
)
async def import_csv(
    file: Annotated[UploadFile, File(...)],
    database_url: Annotated[str, Form(...)],
    table: Annotated[str, Form(...)],
    schema_name: Annotated[str, Form()] = "public",
    delimiter: Annotated[str, Form()] = ",",
    confirm: Annotated[bool, Form()] = False,
) -> ImportResult:
    _require_confirmation(confirm)

    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".csv") as tmp:
        tmp.write(content)
        tmp.flush()
        records = read_csv(Path(tmp.name), delimiter=delimiter)

    return _insert(records, database_url=database_url, schema_name=schema_name, table=table)


@router.post(
    "/json",
    response_model=ImportResult,
    summary="Importer un fichier JSON directement dans une table PostgreSQL",
    description=(
        "Lit un fichier JSON fourni par l'utilisateur (liste d'objets ou objet unique) et insère "
        "les enregistrements tels quels dans la table cible, sans passer par la génération LLM. "
        "L'import n'est jamais implicite : il exige une confirmation explicite (confirm=true)."
    ),
    responses=_RESPONSES,
)
async def import_json(
    file: Annotated[UploadFile, File(...)],
    database_url: Annotated[str, Form(...)],
    table: Annotated[str, Form(...)],
    schema_name: Annotated[str, Form()] = "public",
    confirm: Annotated[bool, Form()] = False,
) -> ImportResult:
    _require_confirmation(confirm)

    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        tmp.write(content)
        tmp.flush()
        records = read_json(Path(tmp.name))

    return _insert(records, database_url=database_url, schema_name=schema_name, table=table)


@router.post(
    "/rest",
    response_model=ImportResult,
    summary="Importer les données d'une API REST directement dans une table PostgreSQL",
    description=(
        "Interroge une API REST (URL, méthode, en-têtes, authentification et chemin "
        "d'extraction fournis explicitement dans `source`, aucun n'est supposé par défaut) "
        "et insère les enregistrements obtenus tels quels dans la table cible, sans passer "
        "par la génération LLM : destiné à charger des données déjà correctes (ex. un "
        "référentiel ou une API tierce). L'import n'est jamais implicite : il exige une "
        "confirmation explicite (confirm=true)."
    ),
    responses=_RESPONSES,
)
def import_rest(request: RestImportRequest) -> ImportResult:
    _require_confirmation(request.confirm)

    records = read_rest(request.source)

    return _insert(records, database_url=request.database_url, schema_name=request.schema_name, table=request.table)
