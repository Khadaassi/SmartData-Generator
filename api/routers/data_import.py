import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.schemas.data_import import ImportResult
from api.schemas.errors import ErrorResponse
from connectors.input import read_csv, read_json
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
    file: UploadFile = File(...),
    database_url: str = Form(...),
    schema_name: str = Form("public"),
    table: str = Form(...),
    delimiter: str = Form(","),
    confirm: bool = Form(False),
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
    file: UploadFile = File(...),
    database_url: str = Form(...),
    schema_name: str = Form("public"),
    table: str = Form(...),
    confirm: bool = Form(False),
) -> ImportResult:
    _require_confirmation(confirm)

    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        tmp.write(content)
        tmp.flush()
        records = read_json(Path(tmp.name))

    return _insert(records, database_url=database_url, schema_name=schema_name, table=table)
