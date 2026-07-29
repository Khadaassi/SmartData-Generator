from fastapi.testclient import TestClient

from api.app import app
from application.document_service import DocumentValidationError, UploadedDocument

client = TestClient(app)

_VALID_MARKDOWN = b"""---
title: Regles de test
category: rule
entity: Produit
---

## Une regle

Contenu de la regle.
"""


def test_upload_documents_returns_indexed_documents(monkeypatch):
    monkeypatch.setattr(
        "api.routers.documents.upload_documents",
        lambda project_id, files: [UploadedDocument(filename="regles.md", chunks_indexed=2)],
    )

    response = client.post(
        "/projects/proj-1/documents",
        files=[("files", ("regles.md", _VALID_MARKDOWN, "text/markdown"))],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["uploaded"] == [{"filename": "regles.md", "chunks_indexed": 2}]


def test_upload_documents_with_invalid_front_matter_returns_422(monkeypatch):
    def _raise(project_id, files):
        raise DocumentValidationError({"bad.md": "Document sans en-tête YAML (front matter manquant)."})

    monkeypatch.setattr("api.routers.documents.upload_documents", _raise)

    response = client.post(
        "/projects/proj-1/documents",
        files=[("files", ("bad.md", b"pas de front matter", "text/markdown"))],
    )

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "invalid_documents"
    assert "bad.md" in body["errors"]


def test_list_documents_returns_document_ids(monkeypatch):
    monkeypatch.setattr("api.routers.documents.list_documents", lambda project_id: ["regles_client"])

    response = client.get("/projects/proj-1/documents")

    assert response.status_code == 200
    assert response.json() == {"documents": ["regles_client"]}


def test_delete_document_returns_204(monkeypatch):
    monkeypatch.setattr("api.routers.documents.delete_document", lambda project_id, filename: None)

    response = client.delete("/projects/proj-1/documents/regles_client.md")

    assert response.status_code == 204
