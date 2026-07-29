from pathlib import Path

import yaml

from rag.chunking import chunk_markdown
from rag.cleaning import clean_text
from rag.schemas import ChunkMetadata, DocumentFrontMatter

_FRONT_MATTER_DELIMITER = "---"


def _parse_front_matter(raw: str) -> tuple[DocumentFrontMatter, str]:
    if not raw.startswith(_FRONT_MATTER_DELIMITER):
        raise ValueError("Document sans en-tête YAML (front matter manquant).")

    _, front_matter_raw, body = raw.split(_FRONT_MATTER_DELIMITER, 2)
    front_matter = DocumentFrontMatter.model_validate(yaml.safe_load(front_matter_raw))
    return front_matter, body


def ingest_document(path: Path, project_id: str) -> list[tuple[str, ChunkMetadata]]:
    """Lit, nettoie et découpe un document ; produit les paires (texte, métadonnées) prêtes à indexer."""
    raw = path.read_text(encoding="utf-8")
    front_matter, body = _parse_front_matter(raw)
    cleaned_body = clean_text(body)

    document_id = path.stem
    results: list[tuple[str, ChunkMetadata]] = []
    for index, chunk in enumerate(chunk_markdown(cleaned_body)):
        metadata = ChunkMetadata(
            document_id=document_id,
            project_id=project_id,
            source_filename=path.name,
            title=front_matter.title,
            category=front_matter.category,
            entity=front_matter.entity,
            chunk_index=index,
            section=chunk.section,
        )
        results.append((chunk.text, metadata))

    return results


def ingest_corpus(corpus_dir: Path, project_id: str) -> list[tuple[str, ChunkMetadata]]:
    """Ingère tous les documents Markdown d'un répertoire (corpus fourni par le client)."""
    results: list[tuple[str, ChunkMetadata]] = []
    for path in sorted(corpus_dir.glob("*.md")):
        results.extend(ingest_document(path, project_id))
    return results
