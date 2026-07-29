import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from application.execution_service import execute
from domain.execution import ExecutionRequest
from domain.generation import GenerationRequest, GenerationResult
from domain.schema import EntitySpec, FieldSpec
from infrastructure.config import get_settings
from persistence.tables import create_all
from reporting.report_service import get_execution_report
from tests.integration._reachability import is_reachable

settings = get_settings()
_db_url = make_url(settings.database_url)

pytestmark = pytest.mark.skipif(
    not is_reachable(_db_url.host, _db_url.port or 5432),
    reason="PostgreSQL non accessible (docker compose -f docker/docker-compose.yml up -d postgres)",
)


@pytest.fixture(scope="module", autouse=True)
def _ensure_tables():
    create_all(create_engine(settings.database_url))


def test_execute_persists_a_retrievable_report(monkeypatch):
    run_id = f"t16_e2e_{uuid.uuid4().hex[:8]}"

    def _fake_run_generation(request):
        return GenerationResult(
            run_id=run_id,
            status="SUCCESS",
            entity=request.entity.name,
            items=[{"nom": "Clavier"}],
            rules_used=[],
            errors=[],
            validation_report=None,
        )

    monkeypatch.setattr("application.execution_service.run_generation", _fake_run_generation)

    entity = EntitySpec(name="Produit", fields=[FieldSpec(name="nom", type="string")])
    generation_request = GenerationRequest(project_id="proj-e2e", entity=entity, count=1)

    result = execute(ExecutionRequest(generation=generation_request, mode="PREVIEW"))

    report = get_execution_report(result.run_id)

    assert report is not None
    assert report.run_id == run_id
    assert report.status == "READY"
    assert report.valid_count == 1
    assert report.duration_seconds >= 0
