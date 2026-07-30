from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from api.schemas.documents import DocumentListResponse, UploadDocumentsResponse
from application.document_service import (
    delete_document,
    list_documents,
    upload_documents,
)

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])


@router.post(
    "",
    response_model=UploadDocumentsResponse,
    summary="Uploader et indexer des documents métier (RAG)",
    description=(
        "Ingère puis indexe un ou plusieurs fichiers Markdown (front matter YAML requis, "
        "cf. rag/corpus/README.md) dans le corpus du projet. Tout ou rien : si un seul "
        "fichier est invalide, aucun n'est écrit ni indexé."
    ),
)
async def upload(project_id: str, files: Annotated[list[UploadFile], File(...)]) -> UploadDocumentsResponse:
    contents = [(file.filename, await file.read()) for file in files]
    uploaded = upload_documents(project_id, contents)
    return UploadDocumentsResponse(
        uploaded=[{"filename": doc.filename, "chunks_indexed": doc.chunks_indexed} for doc in uploaded]
    )


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="Lister les documents indexés d'un projet",
)
def list_all(project_id: str) -> DocumentListResponse:
    return DocumentListResponse(documents=list_documents(project_id))


@router.delete(
    "/{filename}",
    status_code=204,
    summary="Supprimer un document indexé",
)
def delete(project_id: str, filename: str) -> None:
    delete_document(project_id, filename)
