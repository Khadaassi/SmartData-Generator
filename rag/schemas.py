from enum import StrEnum

from pydantic import BaseModel


class DocumentCategory(StrEnum):
    """Cf. functional_technical_scope.md section 6.3."""

    DEFINITION = "definition"
    RULE = "rule"
    CONSTRAINT = "constraint"
    EXAMPLE = "example"
    RELATION = "relation"
    CONVENTION = "convention"
    LIMIT = "limit"
    EXCEPTION = "exception"


class DocumentFrontMatter(BaseModel):
    """Métadonnées déclarées en en-tête YAML d'un document du corpus."""

    title: str
    category: DocumentCategory
    entity: str | None = None


class ChunkMetadata(BaseModel):
    """Métadonnées attachées à chaque chunk indexé dans ChromaDB."""

    document_id: str
    project_id: str
    source_filename: str
    title: str
    category: DocumentCategory
    entity: str | None = None
    chunk_index: int
    section: str | None = None

    def to_chroma_metadata(self) -> dict[str, str | int]:
        data = self.model_dump(exclude_none=True)
        data["category"] = self.category.value
        return data
