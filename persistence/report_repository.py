from sqlalchemy import select
from sqlalchemy.engine import Engine, Row

from domain.report import ExecutionReport
from infrastructure.database import get_engine
from persistence.tables import execution_reports_table


def _row_to_report(row: Row) -> ExecutionReport:
    return ExecutionReport.model_validate(row.report)


def insert_execution_report(report: ExecutionReport, *, engine: Engine | None = None) -> None:
    db_engine = engine or get_engine()
    with db_engine.begin() as conn:
        conn.execute(
            execution_reports_table.insert().values(
                run_id=report.run_id,
                project_id=report.project_id,
                entity=report.entity,
                mode=report.mode,
                status=report.status,
                started_at=report.started_at,
                finished_at=report.finished_at,
                report=report.model_dump(mode="json"),
            )
        )


def find_execution_report(run_id: str, *, engine: Engine | None = None) -> ExecutionReport | None:
    db_engine = engine or get_engine()
    with db_engine.connect() as conn:
        row = conn.execute(select(execution_reports_table).where(execution_reports_table.c.run_id == run_id)).first()
    return _row_to_report(row) if row is not None else None


def list_execution_reports(*, project_id: str | None = None, engine: Engine | None = None) -> list[ExecutionReport]:
    db_engine = engine or get_engine()
    statement = select(execution_reports_table).order_by(execution_reports_table.c.started_at)
    if project_id is not None:
        statement = statement.where(execution_reports_table.c.project_id == project_id)

    with db_engine.connect() as conn:
        rows = conn.execute(statement).all()
    return [_row_to_report(row) for row in rows]
