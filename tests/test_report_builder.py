from datetime import UTC, datetime, timedelta

from domain.execution import ExecutionRequest, ExecutionResult, InsertReport
from domain.generation import GenerationError, GenerationRequest, GenerationResult
from domain.schema import EntitySpec, FieldSpec
from reporting.report_builder import build_execution_report
from validation.schemas import IssueLevel, ValidationIssue, ValidationReport


def _entity() -> EntitySpec:
    return EntitySpec(name="Produit", fields=[FieldSpec(name="nom", type="string")])


def _request(count: int = 5) -> ExecutionRequest:
    generation = GenerationRequest(project_id="proj-1", entity=_entity(), count=count)
    return ExecutionRequest(generation=generation, mode="PREVIEW")


def _validation_report(*, total: int, valid: int) -> ValidationReport:
    return ValidationReport(
        entity="Produit",
        total_items=total,
        valid_items=valid,
        rejected_items=total - valid,
        issues=[],
        valid_data=[{"nom": "x"}] * valid,
        status="PARTIAL" if valid < total else "PASSED",
    )


def _generation_result(**overrides) -> GenerationResult:
    data = {
        "run_id": "run-1",
        "status": "SUCCESS",
        "entity": "Produit",
        "items": [{"nom": "Clavier"}],
        "rules_used": [],
        "errors": [],
        "validation_report": None,
    }
    data.update(overrides)
    return GenerationResult(**data)


def _started_finished(seconds: float = 1.5) -> tuple[datetime, datetime]:
    started = datetime(2026, 1, 1, tzinfo=UTC)
    return started, started + timedelta(seconds=seconds)


def test_build_execution_report_computes_duration():
    started, finished = _started_finished(seconds=2.5)
    result = ExecutionResult(run_id="run-1", mode="PREVIEW", status="READY", generation=_generation_result())

    report = build_execution_report(_request(), result, started, finished)

    assert report.duration_seconds == 2.5
    assert report.started_at == started
    assert report.finished_at == finished


def test_build_execution_report_uses_validation_report_for_volume_counts():
    started, finished = _started_finished()
    generation = _generation_result(
        items=[{"nom": "Clavier"}, {"nom": "Souris"}],
        validation_report=_validation_report(total=5, valid=2),
    )
    result = ExecutionResult(run_id="run-1", mode="PREVIEW", status="READY", generation=generation)

    report = build_execution_report(_request(count=5), result, started, finished)

    assert report.requested_count == 5
    assert report.generated_count == 5
    assert report.valid_count == 2
    assert report.rejected_count == 3


def test_build_execution_report_falls_back_to_zero_counts_without_validation_report():
    # Génération échouée avant la validation (ex. erreur LLM) : aucun rapport de validation.
    started, finished = _started_finished()
    generation = _generation_result(status="FAILED", items=[], validation_report=None)
    result = ExecutionResult(run_id="run-1", mode="PREVIEW", status="VALIDATION_FAILED", generation=generation)

    report = build_execution_report(_request(), result, started, finished)

    assert report.generated_count == 0
    assert report.valid_count == 0
    assert report.rejected_count == 0


def test_build_execution_report_counts_blocking_and_warning_errors_separately():
    started, finished = _started_finished()
    errors = [
        GenerationError(code="rag_unavailable", message="...", stage="rag", blocking=False),
        GenerationError(code="type_error", message="...", stage="validation", blocking=True),
        GenerationError(code="range_violation", message="...", stage="validation", blocking=True),
    ]
    generation = _generation_result(errors=errors)
    result = ExecutionResult(run_id="run-1", mode="PREVIEW", status="READY", generation=generation)

    report = build_execution_report(_request(), result, started, finished)

    assert report.error_count == 3
    assert report.blocking_error_count == 2
    assert report.warning_count == 1
    assert report.errors == errors


def test_build_execution_report_includes_export_path():
    started, finished = _started_finished()
    result = ExecutionResult(
        run_id="run-1", mode="EXPORT", status="EXPORTED", generation=_generation_result(), export_path="/tmp/out.json"
    )

    report = build_execution_report(_request(), result, started, finished)

    assert report.export_path == "/tmp/out.json"
    assert report.insert_report is None


def test_build_execution_report_includes_insert_report():
    started, finished = _started_finished()
    insert_report = InsertReport(table="produits", rows_attempted=3, rows_inserted=3)
    result = ExecutionResult(
        run_id="run-1", mode="INSERT", status="INSERTED", generation=_generation_result(), insert_report=insert_report
    )

    report = build_execution_report(_request(), result, started, finished)

    assert report.insert_report == insert_report


def test_build_execution_report_carries_project_id_and_entity():
    started, finished = _started_finished()
    result = ExecutionResult(run_id="run-1", mode="PREVIEW", status="READY", generation=_generation_result())

    report = build_execution_report(_request(), result, started, finished)

    assert report.project_id == "proj-1"
    assert report.entity == "Produit"


def test_build_execution_report_preserves_validation_report_detail():
    started, finished = _started_finished()
    validation_report = _validation_report(total=3, valid=2)
    validation_report = validation_report.model_copy(
        update={
            "issues": [
                ValidationIssue(level=IssueLevel.ERROR, code="type_error", message="prix invalide", item_index=1)
            ]
        }
    )
    generation = _generation_result(validation_report=validation_report)
    result = ExecutionResult(run_id="run-1", mode="PREVIEW", status="READY", generation=generation)

    report = build_execution_report(_request(), result, started, finished)

    assert report.validation_report == validation_report
    assert report.validation_report.issues[0].code == "type_error"
