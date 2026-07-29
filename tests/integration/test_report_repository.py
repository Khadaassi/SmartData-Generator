import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from domain.execution import ExecutionRequest, ExecutionResult
from domain.generation import GenerationError, GenerationRequest, GenerationResult
from domain.schema import EntitySpec, FieldSpec
from infrastructure.config import get_settings
from persistence.report_repository import (
    find_execution_report,
    insert_execution_report,
    list_execution_reports,
)
from persistence.tables import create_all
from reporting.report_builder import build_execution_report
from tests.integration._reachability import is_reachable

settings = get_settings()
_db_url = make_url(settings.database_url)

pytestmark = pytest.mark.skipif(
    not is_reachable(_db_url.host, _db_url.port or 5432),
    reason="PostgreSQL non accessible (docker compose -f docker/docker-compose.yml up -d postgres)",
)


@pytest.fixture(scope="module")
def engine():
    db_engine = create_engine(settings.database_url)
    create_all(db_engine)
    yield db_engine
    db_engine.dispose()


def _make_report(*, project_id: str, run_id: str, entity: str = "Produit", errors: list[GenerationError] | None = None):
    generation_request = GenerationRequest(
        project_id=project_id, entity=EntitySpec(name=entity, fields=[FieldSpec(name="nom", type="string")]), count=3
    )
    request = ExecutionRequest(generation=generation_request, mode="PREVIEW")
    generation_result = GenerationResult(
        run_id=run_id,
        status="SUCCESS",
        entity=entity,
        items=[{"nom": "Clavier"}],
        rules_used=[],
        errors=errors or [],
        validation_report=None,
    )
    result = ExecutionResult(run_id=run_id, mode="PREVIEW", status="READY", generation=generation_result)

    started = datetime.now(UTC)
    return build_execution_report(request, result, started, started + timedelta(seconds=1))


def test_insert_and_find_execution_report_round_trips(engine):
    run_id = f"t16_{uuid.uuid4().hex[:8]}"
    errors = [GenerationError(code="rag_unavailable", message="chroma indisponible", stage="rag", blocking=False)]
    report = _make_report(project_id="proj-1", run_id=run_id, errors=errors)

    insert_execution_report(report, engine=engine)
    found = find_execution_report(run_id, engine=engine)

    assert found == report
    assert found.error_count == 1
    assert found.blocking_error_count == 0


def test_find_execution_report_returns_none_when_missing(engine):
    assert find_execution_report(f"does-not-exist-{uuid.uuid4().hex}", engine=engine) is None


def test_list_execution_reports_filters_by_project_and_stays_isolated(engine):
    project_a = f"proj-a-{uuid.uuid4().hex[:8]}"
    project_b = f"proj-b-{uuid.uuid4().hex[:8]}"
    report_a = _make_report(project_id=project_a, run_id=f"t16_{uuid.uuid4().hex[:8]}")
    report_b = _make_report(project_id=project_b, run_id=f"t16_{uuid.uuid4().hex[:8]}")

    insert_execution_report(report_a, engine=engine)
    insert_execution_report(report_b, engine=engine)

    reports_for_a = list_execution_reports(project_id=project_a, engine=engine)
    reports_for_b = list_execution_reports(project_id=project_b, engine=engine)

    assert [r.run_id for r in reports_for_a] == [report_a.run_id]
    assert [r.run_id for r in reports_for_b] == [report_b.run_id]
