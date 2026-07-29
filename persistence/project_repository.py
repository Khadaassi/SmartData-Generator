from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.engine import Engine, Row

from domain.project import Project, ProjectConfig
from infrastructure.database import get_engine
from persistence.tables import projects_table


def _row_to_project(row: Row) -> Project:
    return Project(
        id=row.id,
        name=row.name,
        description=row.description,
        config=ProjectConfig.model_validate(row.config),
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def insert_project(project: Project, *, engine: Engine | None = None) -> None:
    db_engine = engine or get_engine()
    with db_engine.begin() as conn:
        conn.execute(
            projects_table.insert().values(
                id=project.id,
                name=project.name,
                description=project.description,
                config=project.config.model_dump(mode="json"),
                is_active=project.is_active,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )


def find_project(project_id: str, *, engine: Engine | None = None) -> Project | None:
    db_engine = engine or get_engine()
    with db_engine.connect() as conn:
        row = conn.execute(select(projects_table).where(projects_table.c.id == project_id)).first()
    return _row_to_project(row) if row is not None else None


def list_all_projects(*, active_only: bool = False, engine: Engine | None = None) -> list[Project]:
    db_engine = engine or get_engine()
    statement = select(projects_table).order_by(projects_table.c.created_at)
    if active_only:
        statement = statement.where(projects_table.c.is_active.is_(True))

    with db_engine.connect() as conn:
        rows = conn.execute(statement).all()
    return [_row_to_project(row) for row in rows]


def update_project_row(project: Project, *, engine: Engine | None = None) -> bool:
    db_engine = engine or get_engine()
    with db_engine.begin() as conn:
        result = conn.execute(
            sa_update(projects_table)
            .where(projects_table.c.id == project.id)
            .values(
                name=project.name,
                description=project.description,
                config=project.config.model_dump(mode="json"),
                is_active=project.is_active,
                updated_at=project.updated_at,
            )
        )
    return result.rowcount > 0


def delete_project_row(project_id: str, *, engine: Engine | None = None) -> bool:
    db_engine = engine or get_engine()
    with db_engine.begin() as conn:
        result = conn.execute(projects_table.delete().where(projects_table.c.id == project_id))
    return result.rowcount > 0
