from pathlib import Path

import rag
from rag.chunking import chunk_markdown
from rag.cleaning import clean_text
from rag.ingestion import ingest_corpus, ingest_document

_EXAMPLES_DIR = Path(rag.__file__).resolve().parent / "corpus" / "examples"


def test_example_corpus_is_present():
    documents = sorted(_EXAMPLES_DIR.glob("*.md"))

    assert len(documents) >= 2


def test_clean_text_normalizes_whitespace():
    raw = "Titre\r\n\r\n\r\nLigne avec espaces   \n\nTexte final"

    cleaned = clean_text(raw)

    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned
    assert not cleaned.endswith(" ")


def test_chunk_markdown_splits_by_section():
    body = "## Première règle\nContenu de la première règle.\n\n## Deuxième règle\nContenu de la deuxième règle."

    chunks = chunk_markdown(body)

    sections = {chunk.section for chunk in chunks}
    assert sections == {"Première règle", "Deuxième règle"}
    assert all(chunk.text.strip() for chunk in chunks)


def test_ingest_document_produces_exploitable_chunks_with_metadata():
    document_path = _EXAMPLES_DIR / "regles_commande.md"

    chunks = ingest_document(document_path, project_id="example")

    assert chunks
    for index, (text, metadata) in enumerate(chunks):
        assert text.strip()
        assert metadata.document_id == "regles_commande"
        assert metadata.project_id == "example"
        assert metadata.source_filename == "regles_commande.md"
        assert metadata.title == "Règles de gestion des commandes"
        assert metadata.category == "rule"
        assert metadata.entity == "Commande"
        assert metadata.chunk_index == index
        assert metadata.section


def test_ingest_corpus_processes_every_document():
    document_count = len(list(_EXAMPLES_DIR.glob("*.md")))

    chunks = ingest_corpus(_EXAMPLES_DIR, project_id="example")

    document_ids = {metadata.document_id for _, metadata in chunks}
    assert len(document_ids) == document_count
    assert len(chunks) > document_count
    assert all(metadata.project_id == "example" for _, metadata in chunks)
