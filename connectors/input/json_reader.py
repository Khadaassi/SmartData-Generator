import json
from pathlib import Path

from connectors.input.errors import DataReaderError
from connectors.input.json_utils import extract_records
from connectors.input.normalize import normalize_records


def read_json(path: Path) -> list[dict]:
    """Lit un fichier JSON et retourne une liste d'enregistrements normalisés.

    Le fichier peut contenir une liste d'objets ou un objet unique (traité comme
    un enregistrement isolé). Le support des structures profondément imbriquées
    reste limité dans le POC (cf. technical_architecture.md section 6.24) : le
    connecteur ne reconstruit pas une structure absente.
    """
    if not path.exists():
        raise DataReaderError(code="file_not_found", message=f"Fichier introuvable : {path}")
    if not path.is_file():
        raise DataReaderError(code="not_a_file", message=f"Le chemin ne correspond pas à un fichier : {path}")

    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataReaderError(code="encoding_error", message=f"Encodage invalide pour {path} : {exc}") from exc

    if not raw.strip():
        raise DataReaderError(code="empty_file", message=f"Fichier JSON vide : {path}")

    try:
        content = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DataReaderError(code="json_parse_error", message=f"Erreur de syntaxe JSON ({path}) : {exc}") from exc

    records = extract_records(content, source=str(path))
    return normalize_records(records)
