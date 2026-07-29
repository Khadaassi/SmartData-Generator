from pydantic import BaseModel


class UploadedDocumentResponse(BaseModel):
    filename: str
    chunks_indexed: int


class UploadDocumentsResponse(BaseModel):
    uploaded: list[UploadedDocumentResponse]


class DocumentListResponse(BaseModel):
    documents: list[str]
