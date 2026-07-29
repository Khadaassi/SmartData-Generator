from fastapi import APIRouter

from application.execution_service import execute
from domain.execution import ExecutionRequest, ExecutionResult

router = APIRouter(prefix="/executions", tags=["executions"])


@router.post(
    "",
    response_model=ExecutionResult,
    summary="Exécuter une génération en mode Preview, Export ou Insert",
    description=(
        "Génère les données pour l'entité fournie, les valide, puis applique le mode demandé. "
        "Preview (par défaut) ne modifie jamais un système externe. Export écrit un fichier "
        "CSV ou JSON. Insert écrit en base PostgreSQL et exige une destination explicite "
        "(`insert_target`) ainsi qu'une confirmation explicite (`confirm_insert=true`) ; "
        "aucune écriture n'a lieu si la génération n'a produit aucune donnée valide. "
        "Les échecs de génération, de validation ou d'écriture ne sont pas des erreurs HTTP : "
        "ils sont décrits dans le corps de la réponse (`status`, `generation.errors`)."
    ),
)
def create_execution(request: ExecutionRequest) -> ExecutionResult:
    return execute(request)
