import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from infrastructure.config import get_settings
from infrastructure.logging import get_logger
from rag.ingestion import ingest_document
from rag.schemas import ChunkMetadata
from rag.vectorstore import delete_document as _delete_indexed_document
from rag.vectorstore import list_documents as _list_indexed_documents
from rag.vectorstore import upsert_chunks

logger = get_logger(__name__)


class DocumentValidationError(Exception):
    """Un ou plusieurs documents uploadés sont invalides (front matter manquant/mal formé).

    Portée par fichier plutôt que par premier échec : le client corrige tout en
    une fois plutôt que de réessayer fichier par fichier.
    """

    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        super().__init__(f"{len(errors)} document(s) invalide(s)")


@dataclass
class UploadedDocument:
    filename: str
    chunks_indexed: int


def _project_dir(project_id: str) -> Path:
    directory = Path(get_settings().documents_storage_dir) / project_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def upload_documents(project_id: str, files: list[tuple[str, bytes]]) -> list[UploadedDocument]:
    """Valide, stocke puis indexe un lot de documents Markdown pour un projet.

    Tout ou rien : si un seul fichier du lot est invalide, rien n'est écrit dans
    le répertoire du projet ni indexé dans ChromaDB — évite un corpus dans un
    état incohérent et une correction fichier par fichier.
    """
    errors: dict[str, str] = {}
    parsed: dict[str, list[tuple[str, ChunkMetadata]]] = {}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for filename, content in files:
            staged_path = tmp_dir / filename
            staged_path.write_bytes(content)
            try:
                parsed[filename] = ingest_document(staged_path, project_id)
            except (ValueError, UnicodeDecodeError) as exc:
                errors[filename] = str(exc)

        if errors:
            raise DocumentValidationError(errors)

        destination_dir = _project_dir(project_id)
        for filename, _ in files:
            shutil.copyfile(tmp_dir / filename, destination_dir / filename)

    all_chunks = [chunk for chunks in parsed.values() for chunk in chunks]
    upsert_chunks(all_chunks)

    logger.info("[%s] %d document(s) indexé(s)", project_id, len(parsed))
    return [UploadedDocument(filename=filename, chunks_indexed=len(chunks)) for filename, chunks in parsed.items()]


def list_documents(project_id: str) -> list[str]:
    return _list_indexed_documents(project_id)


def delete_document(project_id: str, filename: str) -> None:
    _delete_indexed_document(project_id, Path(filename).stem)

    file_path = _project_dir(project_id) / filename
    file_path.unlink(missing_ok=True)

    logger.info("[%s] document supprimé : %s", project_id, filename)
