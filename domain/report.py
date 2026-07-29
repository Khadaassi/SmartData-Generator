from datetime import datetime

from pydantic import BaseModel

from domain.execution import ExecutionMode, ExecutionStatus, InsertReport
from domain.generation import GenerationError
from validation.schemas import ValidationReport


class ExecutionReport(BaseModel):
    """Rapport détaillé d'une exécution, produit systématiquement pour assurer la
    traçabilité des traitements (cf. technical_architecture.md section 6.29,
    Execution Reporter)."""

    run_id: str
    project_id: str
    entity: str
    mode: ExecutionMode
    status: ExecutionStatus

    started_at: datetime
    finished_at: datetime
    duration_seconds: float

    # Comptabilisation des données générées : `generated_count` est le volume produit
    # avant validation, `valid_count`/`rejected_count` le résultat de la validation.
    requested_count: int
    generated_count: int
    valid_count: int
    rejected_count: int

    # Comptabilisation des erreurs, toutes étapes confondues (RAG, génération, validation,
    # export, insertion) — `blocking_error_count` est le sous-ensemble ayant empêché une écriture.
    error_count: int
    blocking_error_count: int
    warning_count: int
    errors: list[GenerationError]

    validation_report: ValidationReport | None = None
    export_path: str | None = None
    insert_report: InsertReport | None = None
