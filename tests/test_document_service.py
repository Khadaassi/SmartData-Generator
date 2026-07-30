import pytest

from application.document_service import (
    DocumentValidationError,
    delete_document,
    list_documents,
    upload_documents,
)
from infrastructure.config import Settings

_VALID_MARKDOWN = b"""---
title: Regles de test
category: rule
entity: Produit
---

## Une regle

Contenu de la regle.
"""


@pytest.fixture(autouse=True)
def _storage_dir(tmp_path, monkeypatch):
    settings = Settings(documents_storage_dir=str(tmp_path))
    monkeypatch.setattr("application.document_service.get_settings", lambda: settings)
    return tmp_path


def test_upload_documents_writes_files_and_indexes_chunks(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setattr(
        "application.document_service.upsert_chunks",
        lambda chunks: captured.setdefault("chunks", chunks) and len(chunks),
    )

    uploaded = upload_documents("proj-1", [("regles.md", _VALID_MARKDOWN)])

    assert [doc.filename for doc in uploaded] == ["regles.md"]
    assert uploaded[0].chunks_indexed == 1
    assert (tmp_path / "proj-1" / "regles.md").read_bytes() == _VALID_MARKDOWN
    assert len(captured["chunks"]) == 1


def test_upload_documents_rejects_the_whole_batch_when_one_file_is_invalid(monkeypatch, tmp_path):
    upsert_called = []
    monkeypatch.setattr("application.document_service.upsert_chunks", lambda chunks: upsert_called.append(chunks))

    with pytest.raises(DocumentValidationError) as exc_info:
        upload_documents(
            "proj-1",
            [("good.md", _VALID_MARKDOWN), ("bad.md", b"pas de front matter")],
        )

    assert "bad.md" in exc_info.value.errors
    assert not upsert_called
    assert not (tmp_path / "proj-1").exists() or not list((tmp_path / "proj-1").iterdir())


def test_list_documents_delegates_to_vectorstore(monkeypatch):
    monkeypatch.setattr(
        "application.document_service._list_indexed_documents", lambda project_id: ["regles_client"]
    )

    assert list_documents("proj-1") == ["regles_client"]


def test_delete_document_removes_index_entries_and_file(monkeypatch, tmp_path):
    (tmp_path / "proj-1").mkdir()
    (tmp_path / "proj-1" / "regles_client.md").write_bytes(_VALID_MARKDOWN)

    deleted = {}
    monkeypatch.setattr(
        "application.document_service._delete_indexed_document",
        lambda project_id, document_id: deleted.setdefault("args", (project_id, document_id)),
    )

    delete_document("proj-1", "regles_client.md")

    assert deleted["args"] == ("proj-1", "regles_client")
    assert not (tmp_path / "proj-1" / "regles_client.md").exists()


def test_delete_document_does_not_fail_when_file_absent(monkeypatch, tmp_path):
    monkeypatch.setattr("application.document_service._delete_indexed_document", lambda project_id, document_id: None)

    delete_document("proj-1", "does-not-exist.md")  # ne lève pas
