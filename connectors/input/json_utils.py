from typing import Any

from connectors.input.errors import DataReaderError


def extract_records(content: Any, source: str) -> list[dict]:
    """Interprète un contenu JSON déjà parsé (fichier ou réponse HTTP) comme une liste d'enregistrements.

    Accepte une liste d'objets ou un objet unique (traité comme un enregistrement
    isolé) ; ne reconstruit jamais une structure absente (cf. technical_architecture.md
    section 6.24).
    """
    if isinstance(content, list):
        records = content
    elif isinstance(content, dict):
        records = [content]
    else:
        raise DataReaderError(
            code="invalid_json_structure",
            message=f"Structure JSON non supportée dans {source} : une liste ou un objet est attendu.",
        )

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise DataReaderError(
                code="invalid_json_structure",
                message=f"L'élément {index} de {source} n'est pas un objet JSON.",
            )

    return records
