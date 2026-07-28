from fastapi import APIRouter

from api.dependencies import SettingsDep
from api.schemas.health import HealthResponse
from infrastructure.config import get_project_version

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Vérifier la disponibilité du service")
def get_health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="smartdata-generator",
        version=get_project_version(),
        environment=settings.app_env,
    )
