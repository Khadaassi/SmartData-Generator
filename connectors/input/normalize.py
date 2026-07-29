from typing import Any


def normalize_records(records: list[dict]) -> list[dict]:
    """Uniformise des enregistrements bruts issus d'un connecteur (CSV ou JSON).

    Les clés sont nettoyées des espaces superflus et les chaînes vides sont
    ramenées à None, afin que le Validation Engine traite de façon identique
    une valeur manquante quelle que soit sa source (cf. technical_architecture.md
    section 6.23/6.24 : les connecteurs ne doivent pas inventer les types).
    """
    return [_normalize_record(record) for record in records]


def _normalize_record(record: dict) -> dict:
    return {(key.strip() if isinstance(key, str) else key): _normalize_value(value) for key, value in record.items()}


def _normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, dict):
        return _normalize_record(value)
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    return value
