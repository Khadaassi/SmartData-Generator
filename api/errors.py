from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.schemas.errors import ErrorResponse
from application.document_service import DocumentValidationError
from application.project_service import ProjectNotFoundError
from connectors.input import DataReaderError
from connectors.postgres import DataWriteError, SchemaReaderError
from infrastructure.logging import get_logger

logger = get_logger(__name__)

# Statuts volontairement simplifiés par famille d'erreur connecteur : le détail
# (code) reste disponible dans le corps de la réponse pour un traitement fin côté client.
_STATUS_BY_EXCEPTION: dict[type[Exception], int] = {
    SchemaReaderError: 502,
    ProjectNotFoundError: 404,
    DataReaderError: 400,
    DataWriteError: 502,
}


def register_exception_handlers(app: FastAPI) -> None:
    """Convertit les erreurs connues des connecteurs en réponses HTTP structurées.

    Une erreur non anticipée reste couverte par un handler générique (500) afin
    qu'aucune trace interne ne fuite vers le client (cf. functional_technical_scope.md
    section 19, catégorie "erreur interne").
    """
    for exc_type, status_code in _STATUS_BY_EXCEPTION.items():
        app.add_exception_handler(exc_type, _connector_error_handler(status_code))
    app.add_exception_handler(DocumentValidationError, _document_validation_error_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)


def _connector_error_handler(status_code: int):
    async def handler(request: Request, exc) -> JSONResponse:
        logger.error("%s %s -> %s : %s", request.method, request.url.path, exc.code, exc.message)
        return JSONResponse(
            status_code=status_code, content=ErrorResponse(code=exc.code, message=exc.message).model_dump()
        )

    return handler


async def _document_validation_error_handler(request: Request, exc: DocumentValidationError) -> JSONResponse:
    logger.warning("%s %s -> document(s) invalide(s) : %s", request.method, request.url.path, exc.errors)
    return JSONResponse(
        status_code=422,
        content={
            "code": "invalid_documents",
            "message": "Un ou plusieurs documents sont invalides.",
            "errors": exc.errors,
        },
    )


async def _unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Erreur interne inattendue sur %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(code="internal_error", message="Une erreur interne est survenue.").model_dump(),
    )
