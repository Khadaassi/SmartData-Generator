from datetime import datetime

from domain.execution import ExecutionRequest, ExecutionResult
from domain.report import ExecutionReport


def build_execution_report(
    request: ExecutionRequest, result: ExecutionResult, started_at: datetime, finished_at: datetime
) -> ExecutionReport:
    """Construit le rapport détaillé d'une exécution à partir de son résultat.

    Les comptages de volumétrie proviennent du rapport de validation quand il existe
    (nombre d'objets générés avant filtrage, valides, rejetés) ; si la génération a
    échoué avant d'atteindre la validation (ex. erreur LLM), ils retombent à zéro.
    """
    generation = result.generation
    validation_report = generation.validation_report

    generated_count = validation_report.total_items if validation_report is not None else 0
    valid_count = validation_report.valid_items if validation_report is not None else len(generation.items)
    rejected_count = validation_report.rejected_items if validation_report is not None else 0

    blocking_errors = [error for error in generation.errors if error.blocking]

    return ExecutionReport(
        run_id=result.run_id,
        project_id=request.generation.project_id,
        entity=generation.entity,
        mode=result.mode,
        status=result.status,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=(finished_at - started_at).total_seconds(),
        requested_count=request.generation.count,
        generated_count=generated_count,
        valid_count=valid_count,
        rejected_count=rejected_count,
        error_count=len(generation.errors),
        blocking_error_count=len(blocking_errors),
        warning_count=len(generation.errors) - len(blocking_errors),
        errors=generation.errors,
        validation_report=validation_report,
        export_path=result.export_path,
        insert_report=result.insert_report,
    )
