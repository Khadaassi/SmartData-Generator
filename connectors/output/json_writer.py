import json
from pathlib import Path

from connectors.output.errors import DataWriterError


def write_json(items: list[dict], path: Path) -> None:
    """Écrit une liste d'enregistrements dans un fichier JSON (tableau d'objets)."""
    if not items:
        raise DataWriterError(code="no_data", message="Aucune donnée à exporter.")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise DataWriterError(code="write_error", message=f"Erreur d'écriture du fichier {path} : {exc}") from exc
