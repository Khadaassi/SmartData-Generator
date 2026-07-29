from typing import Literal

from pydantic import BaseModel

from domain.generation import GenerationRequest, GenerationResult

ExecutionMode = Literal["PREVIEW", "EXPORT", "INSERT"]
ExportFormat = Literal["csv", "json"]

# Cf. technical_architecture.md section 6.6 (statuts conceptuels d'exécution) :
# seul le sous-ensemble atteignable de façon synchrone par ce service est repris ici.
ExecutionStatus = Literal["READY", "VALIDATION_FAILED", "EXPORTED", "INSERTED", "FAILED"]


class PostgresInsertTarget(BaseModel):
    """Destination d'insertion explicite, distincte du stockage interne de
    SmartData Generator (cf. technical_architecture.md section 6.30) : rien n'est
    supposé, l'appelant doit fournir la base, le schéma et la table cibles."""

    database_url: str
    table: str
    schema_name: str = "public"


class ExecutionRequest(BaseModel):
    """Requête d'exécution : une génération, exécutée dans l'un des trois modes.

    Le mode Preview est le comportement par défaut (cf. functional_technical_scope.md
    section 8.1) ; Export et Insert exécutent les mêmes étapes puis ajoutent une
    opération d'écriture soumise à ses propres contrôles.
    """

    generation: GenerationRequest
    mode: ExecutionMode = "PREVIEW"

    # mode="EXPORT"
    export_format: ExportFormat = "json"

    # mode="INSERT" : l'insertion n'est jamais implicite, elle exige une confirmation explicite
    # (cf. functional_technical_scope.md section 6.9 / 12.5).
    insert_target: PostgresInsertTarget | None = None
    confirm_insert: bool = False


class InsertReport(BaseModel):
    table: str
    rows_attempted: int
    rows_inserted: int


class ExecutionResult(BaseModel):
    run_id: str
    mode: ExecutionMode
    status: ExecutionStatus
    generation: GenerationResult
    export_path: str | None = None
    insert_report: InsertReport | None = None
