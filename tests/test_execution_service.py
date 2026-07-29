import json
from pathlib import Path

import pytest

from application.execution_service import execute
from connectors.postgres import DataWriteError
from domain.execution import ExecutionRequest, PostgresInsertTarget
from domain.generation import GenerationRequest, GenerationResult
from domain.project import ProjectConfig
from domain.schema import EntitySpec, FieldSpec


@pytest.fixture(autouse=True)
def _no_report_persistence(monkeypatch):
    # La persistance du rapport touche la base interne : hors de portée de ces tests unitaires,
    # qui portent sur le comportement des modes eux-mêmes (cf. test_report_builder.py /
    # tests/integration/test_report_repository.py pour le rapport lui-même).
    monkeypatch.setattr("application.execution_service.save_execution_report", lambda report: None)


@pytest.fixture(autouse=True)
def _no_project_lookup(monkeypatch):
    # Ces tests portent sur le comportement des modes (Preview/Export/Insert), pas sur les
    # règles métier d'un projet réel (cf. test_api_executions.py pour la fusion des règles) :
    # un projet vide évite d'avoir à créer une vraie ligne projet ici.
    monkeypatch.setattr("application.execution_service.load_project_config", lambda project_id: ProjectConfig())


def _entity() -> EntitySpec:
    return EntitySpec(name="Produit", fields=[FieldSpec(name="nom", type="string")])


def _generation_request() -> GenerationRequest:
    return GenerationRequest(project_id="proj-1", entity=_entity(), count=2)


def _success_result(items: list[dict] | None = None) -> GenerationResult:
    return GenerationResult(
        run_id="run-1",
        status="SUCCESS",
        entity="Produit",
        items=items if items is not None else [{"nom": "Clavier"}, {"nom": "Souris"}],
        rules_used=[],
        errors=[],
        validation_report=None,
    )


def _failed_result() -> GenerationResult:
    return GenerationResult(
        run_id="run-1", status="FAILED", entity="Produit", items=[], rules_used=[], errors=[], validation_report=None
    )


def _patch_generation(monkeypatch, result: GenerationResult) -> None:
    monkeypatch.setattr("application.execution_service.run_generation", lambda request: result)


def _patch_export_dir(monkeypatch, tmp_path: Path) -> None:
    class _FakeSettings:
        export_output_dir = str(tmp_path)

    monkeypatch.setattr("application.execution_service.get_settings", lambda: _FakeSettings())


def _insert_target() -> PostgresInsertTarget:
    return PostgresInsertTarget(database_url="postgresql+psycopg://u:p@localhost/db", table="produits")


# --- PREVIEW ---


def test_preview_mode_returns_ready_when_generation_succeeds(monkeypatch):
    _patch_generation(monkeypatch, _success_result())

    result = execute(ExecutionRequest(generation=_generation_request(), mode="PREVIEW"))

    assert result.status == "READY"
    assert result.generation.items == [{"nom": "Clavier"}, {"nom": "Souris"}]
    assert result.export_path is None
    assert result.insert_report is None


def test_preview_mode_returns_validation_failed_when_generation_fails(monkeypatch):
    _patch_generation(monkeypatch, _failed_result())

    result = execute(ExecutionRequest(generation=_generation_request(), mode="PREVIEW"))

    assert result.status == "VALIDATION_FAILED"


# --- EXPORT ---


def test_export_mode_writes_json_file(monkeypatch, tmp_path):
    _patch_generation(monkeypatch, _success_result())
    _patch_export_dir(monkeypatch, tmp_path)

    result = execute(ExecutionRequest(generation=_generation_request(), mode="EXPORT", export_format="json"))

    assert result.status == "EXPORTED"
    exported = Path(result.export_path)
    assert json.loads(exported.read_text(encoding="utf-8")) == [{"nom": "Clavier"}, {"nom": "Souris"}]


def test_export_mode_writes_csv_file(monkeypatch, tmp_path):
    _patch_generation(monkeypatch, _success_result())
    _patch_export_dir(monkeypatch, tmp_path)

    result = execute(ExecutionRequest(generation=_generation_request(), mode="EXPORT", export_format="csv"))

    assert result.status == "EXPORTED"
    assert Path(result.export_path).exists()


def test_export_mode_blocked_when_generation_failed(monkeypatch, tmp_path):
    _patch_generation(monkeypatch, _failed_result())
    _patch_export_dir(monkeypatch, tmp_path)

    result = execute(ExecutionRequest(generation=_generation_request(), mode="EXPORT"))

    assert result.status == "VALIDATION_FAILED"
    assert result.export_path is None
    assert list(tmp_path.iterdir()) == []


# --- INSERT : contrôles de sécurité ---


def test_insert_mode_requires_explicit_target(monkeypatch):
    _patch_generation(monkeypatch, _success_result())

    result = execute(ExecutionRequest(generation=_generation_request(), mode="INSERT", confirm_insert=True))

    assert result.status == "FAILED"
    assert any(error.code == "insert_target_missing" for error in result.generation.errors)


def test_insert_mode_requires_explicit_confirmation(monkeypatch):
    _patch_generation(monkeypatch, _success_result())

    result = execute(
        ExecutionRequest(
            generation=_generation_request(), mode="INSERT", insert_target=_insert_target(), confirm_insert=False
        )
    )

    assert result.status == "FAILED"
    assert any(error.code == "insert_not_confirmed" for error in result.generation.errors)


def test_insert_mode_blocked_when_generation_failed(monkeypatch):
    _patch_generation(monkeypatch, _failed_result())

    result = execute(
        ExecutionRequest(
            generation=_generation_request(), mode="INSERT", insert_target=_insert_target(), confirm_insert=True
        )
    )

    assert result.status == "VALIDATION_FAILED"


def test_insert_mode_succeeds_with_target_and_confirmation(monkeypatch):
    _patch_generation(monkeypatch, _success_result())
    monkeypatch.setattr("application.execution_service.insert_records", lambda *args, **kwargs: 2)

    result = execute(
        ExecutionRequest(
            generation=_generation_request(), mode="INSERT", insert_target=_insert_target(), confirm_insert=True
        )
    )

    assert result.status == "INSERTED"
    assert result.insert_report.table == "produits"
    assert result.insert_report.rows_attempted == 2
    assert result.insert_report.rows_inserted == 2


def test_insert_mode_reports_rollback_as_failure(monkeypatch):
    _patch_generation(monkeypatch, _success_result())

    def _raise(*args, **kwargs):
        raise DataWriteError(code="integrity_error", message="contrainte violée")

    monkeypatch.setattr("application.execution_service.insert_records", _raise)

    result = execute(
        ExecutionRequest(
            generation=_generation_request(), mode="INSERT", insert_target=_insert_target(), confirm_insert=True
        )
    )

    assert result.status == "FAILED"
    assert result.insert_report is None
    assert any(error.code == "integrity_error" for error in result.generation.errors)


# --- Rapport d'exécution ---


def test_execute_builds_and_persists_a_report_for_every_call(monkeypatch):
    _patch_generation(monkeypatch, _success_result())
    captured = {}
    monkeypatch.setattr("application.execution_service.save_execution_report", lambda report: captured.setdefault("report", report))

    result = execute(ExecutionRequest(generation=_generation_request(), mode="PREVIEW"))

    report = captured["report"]
    assert report.run_id == result.run_id
    assert report.mode == "PREVIEW"
    assert report.status == "READY"
    assert report.duration_seconds >= 0
    assert report.requested_count == 2


def test_execute_still_returns_a_result_when_report_persistence_fails(monkeypatch):
    _patch_generation(monkeypatch, _success_result())

    def _raise(report):
        raise RuntimeError("base interne indisponible")

    monkeypatch.setattr("application.execution_service.save_execution_report", _raise)

    result = execute(ExecutionRequest(generation=_generation_request(), mode="PREVIEW"))

    assert result.status == "READY"  # le résultat métier n'est pas affecté par l'échec du rapport
