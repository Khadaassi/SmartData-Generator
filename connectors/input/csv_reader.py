import csv
from pathlib import Path

from connectors.input.errors import DataReaderError
from connectors.input.normalize import normalize_records


def read_csv(path: Path, *, delimiter: str = ",") -> list[dict]:
    """Lit un fichier CSV et retourne une liste d'enregistrements normalisés.

    Les valeurs restent des chaînes (ou None si vides) : le connecteur ne doit
    pas inventer les types lorsqu'ils ne peuvent pas être déterminés
    (cf. technical_architecture.md section 6.23) ; la conversion de type relève
    du Schema Analyzer et du Validation Engine.
    """
    if not path.exists():
        raise DataReaderError(code="file_not_found", message=f"Fichier introuvable : {path}")
    if not path.is_file():
        raise DataReaderError(code="not_a_file", message=f"Le chemin ne correspond pas à un fichier : {path}")

    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            if reader.fieldnames is None:
                raise DataReaderError(code="empty_file", message=f"Fichier CSV vide : {path}")

            rows = []
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    raise DataReaderError(
                        code="malformed_row",
                        message=f"Ligne {line_number} de {path} contient plus de colonnes que d'en-têtes.",
                    )
                rows.append(row)
    except UnicodeDecodeError as exc:
        raise DataReaderError(code="encoding_error", message=f"Encodage invalide pour {path} : {exc}") from exc
    except csv.Error as exc:
        raise DataReaderError(code="csv_parse_error", message=f"Erreur de lecture CSV ({path}) : {exc}") from exc

    return normalize_records(rows)
