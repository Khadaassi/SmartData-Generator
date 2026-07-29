import csv
from pathlib import Path

from connectors.output.errors import DataWriterError


def write_csv(items: list[dict], path: Path) -> None:
    """Écrit une liste d'enregistrements dans un fichier CSV.

    L'en-tête est l'union ordonnée des clés de tous les enregistrements, pour ne
    perdre aucune colonne lorsque certains objets ont des champs optionnels absents.
    """
    if not items:
        raise DataWriterError(code="no_data", message="Aucune donnée à exporter.")

    fieldnames: list[str] = []
    seen: set[str] = set()
    for item in items:
        for key in item:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(items)
    except OSError as exc:
        raise DataWriterError(code="write_error", message=f"Erreur d'écriture du fichier {path} : {exc}") from exc
