from datetime import UTC, datetime
from pathlib import Path

from agents.generation_agent import run_generation
from connectors.output import DataWriterError, write_csv, write_json
from connectors.postgres import DataWriteError, insert_records
from domain.execution import ExecutionRequest, ExecutionResult, InsertReport
from domain.generation import GenerationError, GenerationResult
from domain.report import ExecutionReport
from infrastructure.config import get_settings
from infrastructure.logging import get_logger
from reporting.report_builder import build_execution_report
from reporting.report_service import save_execution_report

logger = get_logger(__name__)


def _blocked_by_validation(result: GenerationResult) -> bool:
    """Aucune donnée exploitable : rien à prévisualiser, exporter ou insérer.

    `result.items` ne contient déjà que les objets valides (les rejets sont filtrés
    en amont par le Validation Engine) : un statut FAILED ou une liste vide signifient
    qu'aucun objet n'a survécu à la validation (cf. functional_technical_scope.md
    section 11.7/11.8, absence d'erreur bloquante requise avant écriture).
    """
    return result.status == "FAILED" or not result.items


def _build_export_path(run_id: str, entity: str, export_format: str) -> Path:
    directory = Path(get_settings().export_output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{entity}_{run_id}.{export_format}"


def execute(request: ExecutionRequest) -> ExecutionResult:
    """Exécute une génération dans le mode demandé (Preview, Export ou Insert).

    Chaque exécution produit systématiquement un rapport détaillé (durée, volumes,
    erreurs) enregistré indépendamment du résultat métier, pour assurer la
    traçabilité des traitements (cf. technical_architecture.md section 6.29).
    """
    started_at = datetime.now(UTC)
    result = _dispatch(request)
    finished_at = datetime.now(UTC)

    _record_execution_report(request, result, started_at, finished_at)

    return result


def _record_execution_report(
    request: ExecutionRequest, result: ExecutionResult, started_at: datetime, finished_at: datetime
) -> None:
    report: ExecutionReport = build_execution_report(request, result, started_at, finished_at)
    try:
        save_execution_report(report)
    except Exception:
        logger.exception("[%s] échec de l'enregistrement du rapport d'exécution", report.run_id)


def _dispatch(request: ExecutionRequest) -> ExecutionResult:
    """Preview est le comportement par défaut et ne modifie jamais un système externe.

    Export et Insert réutilisent le même résultat de génération/validation puis
    ajoutent une opération d'écriture propre, chacune avec ses propres contrôles.
    """
    generation_result = run_generation(request.generation)
    run_id = generation_result.run_id

    logger.info(
        "[%s] exécution mode=%s entity=%s statut_génération=%s objets_valides=%d",
        run_id,
        request.mode,
        request.generation.entity.name,
        generation_result.status,
        len(generation_result.items),
    )

    if _blocked_by_validation(generation_result):
        logger.warning(
            "[%s] mode=%s arrêté avant écriture : aucune donnée valide (statut=%s)",
            run_id,
            request.mode,
            generation_result.status,
        )
        return ExecutionResult(run_id=run_id, mode=request.mode, status="VALIDATION_FAILED", generation=generation_result)

    validation_report = generation_result.validation_report
    if validation_report is not None and validation_report.rejected_items:
        logger.warning(
            "[%s] mode=%s : %d/%d objet(s) rejeté(s) par la validation, poursuite avec %d objet(s) valide(s)",
            run_id,
            request.mode,
            validation_report.rejected_items,
            validation_report.total_items,
            len(generation_result.items),
        )

    if request.mode == "PREVIEW":
        logger.info("[%s] preview prêt : %d objet(s)", run_id, len(generation_result.items))
        return ExecutionResult(run_id=run_id, mode=request.mode, status="READY", generation=generation_result)

    if request.mode == "EXPORT":
        return _execute_export(request, generation_result)

    return _execute_insert(request, generation_result)


def _execute_export(request: ExecutionRequest, generation_result: GenerationResult) -> ExecutionResult:
    run_id = generation_result.run_id
    path = _build_export_path(run_id, generation_result.entity, request.export_format)

    try:
        if request.export_format == "csv":
            write_csv(generation_result.items, path)
        else:
            write_json(generation_result.items, path)
    except DataWriterError as exc:
        logger.error("[%s] export échoué : %s", run_id, exc.message)
        generation_result.errors.append(
            GenerationError(code=exc.code, message=exc.message, stage="export", blocking=True)
        )
        return ExecutionResult(run_id=run_id, mode=request.mode, status="FAILED", generation=generation_result)

    logger.info("[%s] export réussi : %d objet(s) -> %s", run_id, len(generation_result.items), path)
    return ExecutionResult(
        run_id=run_id, mode=request.mode, status="EXPORTED", generation=generation_result, export_path=str(path)
    )


def _execute_insert(request: ExecutionRequest, generation_result: GenerationResult) -> ExecutionResult:
    """Applique les contrôles de sécurité avant toute écriture PostgreSQL.

    Une insertion n'est jamais implicite : elle exige une destination explicite et
    une confirmation explicite (`confirm_insert=True`), en plus de l'absence
    d'erreur bloquante déjà vérifiée par l'appelant (cf. functional_technical_scope.md
    section 6.9, "l'insertion n'est jamais déclenchée automatiquement").
    """
    run_id = generation_result.run_id

    if request.insert_target is None:
        logger.error("[%s] insertion refusée : aucune destination configurée", run_id)
        generation_result.errors.append(
            GenerationError(
                code="insert_target_missing",
                message="Aucune destination d'insertion (insert_target) n'a été fournie.",
                stage="insert",
                blocking=True,
            )
        )
        return ExecutionResult(run_id=run_id, mode=request.mode, status="FAILED", generation=generation_result)

    if not request.confirm_insert:
        logger.warning("[%s] insertion refusée : confirmation explicite absente (confirm_insert=False)", run_id)
        generation_result.errors.append(
            GenerationError(
                code="insert_not_confirmed",
                message="L'insertion requiert une confirmation explicite (confirm_insert=True).",
                stage="insert",
                blocking=True,
            )
        )
        return ExecutionResult(run_id=run_id, mode=request.mode, status="FAILED", generation=generation_result)

    target = request.insert_target
    logger.info(
        "[%s] insertion demandée table=%s.%s objets=%d",
        run_id,
        target.schema_name,
        target.table,
        len(generation_result.items),
    )

    try:
        rows_inserted = insert_records(
            target.database_url, schema=target.schema_name, table=target.table, items=generation_result.items
        )
    except DataWriteError as exc:
        logger.error("[%s] insertion échouée, rollback effectué : %s", run_id, exc.message)
        generation_result.errors.append(
            GenerationError(code=exc.code, message=exc.message, stage="insert", blocking=True)
        )
        return ExecutionResult(run_id=run_id, mode=request.mode, status="FAILED", generation=generation_result)

    logger.info(
        "[%s] insertion réussie : %d/%d ligne(s) insérée(s) dans %s.%s",
        run_id,
        rows_inserted,
        len(generation_result.items),
        target.schema_name,
        target.table,
    )
    return ExecutionResult(
        run_id=run_id,
        mode=request.mode,
        status="INSERTED",
        generation=generation_result,
        insert_report=InsertReport(
            table=target.table, rows_attempted=len(generation_result.items), rows_inserted=rows_inserted
        ),
    )
