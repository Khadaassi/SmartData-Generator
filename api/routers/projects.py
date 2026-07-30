from fastapi import APIRouter

from api.schemas.projects import CreateProjectRequest, UpdateRulesRequest
from application.project_service import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project_config,
)
from domain.project import Project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=Project,
    status_code=201,
    summary="Créer un projet",
    description="Crée un nouveau projet, prêt à recevoir des documents métier et des règles.",
)
def create(request: CreateProjectRequest) -> Project:
    return create_project(request.name, description=request.description)


@router.get(
    "",
    response_model=list[Project],
    summary="Lister les projets",
)
def list_all(active_only: bool = False) -> list[Project]:
    return list_projects(active_only=active_only)


@router.get(
    "/{project_id}",
    response_model=Project,
    summary="Récupérer un projet",
)
def get_one(project_id: str) -> Project:
    return get_project(project_id)


@router.put(
    "/{project_id}/rules",
    response_model=Project,
    summary="Remplacer les règles métier d'un projet",
)
def replace_rules(project_id: str, request: UpdateRulesRequest) -> Project:
    project = get_project(project_id)
    config = project.config.model_copy(update={"rules": request.rules})
    return update_project_config(project_id, config)


@router.delete(
    "/{project_id}",
    status_code=204,
    summary="Supprimer un projet",
)
def delete(project_id: str) -> None:
    delete_project(project_id)
