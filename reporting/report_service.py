from domain.report import ExecutionReport
from infrastructure.logging import get_logger
from persistence.report_repository import (
    find_execution_report,
    insert_execution_report,
    list_execution_reports,
)

logger = get_logger(__name__)


def save_execution_report(report: ExecutionReport) -> None:
    insert_execution_report(report)
    logger.info(
        "[%s] rapport d'exécution enregistré : mode=%s statut=%s durée=%.2fs "
        "générés=%d valides=%d rejetés=%d erreurs=%d (%d bloquante(s))",
        report.run_id,
        report.mode,
        report.status,
        report.duration_seconds,
        report.generated_count,
        report.valid_count,
        report.rejected_count,
        report.error_count,
        report.blocking_error_count,
    )


def get_execution_report(run_id: str) -> ExecutionReport | None:
    return find_execution_report(run_id)


def list_project_execution_reports(project_id: str) -> list[ExecutionReport]:
    return list_execution_reports(project_id=project_id)
