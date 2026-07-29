from datetime import UTC, datetime
from uuid import uuid4

from domain.project import Project, ProjectConfig
from infrastructure.logging import get_logger
from persistence.project_repository import (
    delete_project_row,
    find_project,
    insert_project,
    list_all_projects,
    update_project_row,
)

logger = get_logger(__name__)


class ProjectNotFoundError(Exception):
    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Projet introuvable : {project_id}")


def create_project(name: str, *, description: str | None = None, config: ProjectConfig | None = None) -> Project:
    now = datetime.now(UTC)
    project = Project(
        id=uuid4().hex,
        name=name,
        description=description,
        config=config or ProjectConfig(),
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    insert_project(project)
    logger.info("[%s] projet créé : %s", project.id, project.name)
    return project


def get_project(project_id: str) -> Project:
    project = find_project(project_id)
    if project is None:
        raise ProjectNotFoundError(project_id)
    return project


def list_projects(*, active_only: bool = False) -> list[Project]:
    return list_all_projects(active_only=active_only)


def load_project_config(project_id: str) -> ProjectConfig:
    """Charge la configuration d'un projet, prête à être utilisée pour une génération.

    Chaque appel relit le projet identifié par son id : deux projets ne partagent et
    ne peuvent jamais faire fuiter leur configuration l'un vers l'autre (isolation par id).
    """
    return get_project(project_id).config


def update_project_config(project_id: str, config: ProjectConfig) -> Project:
    project = get_project(project_id)
    updated = project.model_copy(update={"config": config, "updated_at": datetime.now(UTC)})
    update_project_row(updated)
    logger.info("[%s] configuration mise à jour", project_id)
    return updated


def set_project_active(project_id: str, is_active: bool) -> Project:
    project = get_project(project_id)
    updated = project.model_copy(update={"is_active": is_active, "updated_at": datetime.now(UTC)})
    update_project_row(updated)
    logger.info("[%s] projet %s", project_id, "activé" if is_active else "désactivé")
    return updated


def delete_project(project_id: str) -> None:
    if not delete_project_row(project_id):
        raise ProjectNotFoundError(project_id)
    logger.info("[%s] projet supprimé", project_id)
