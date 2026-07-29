from sqlalchemy import Boolean, Column, DateTime, MetaData, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine

metadata = MetaData()

projects_table = Table(
    "projects",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=True),
    Column("config", JSONB, nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

# Colonnes dupliquées depuis le JSONB (project_id, status, dates) pour permettre de filtrer
# et lister sans avoir à interroger le contenu du rapport ; le détail complet reste dans `report`.
execution_reports_table = Table(
    "execution_reports",
    metadata,
    Column("run_id", String, primary_key=True),
    Column("project_id", String, nullable=False),
    Column("entity", String, nullable=False),
    Column("mode", String, nullable=False),
    Column("status", String, nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("finished_at", DateTime(timezone=True), nullable=False),
    Column("report", JSONB, nullable=False),
)


def create_all(engine: Engine) -> None:
    """Crée les tables internes manquantes. Idempotent : n'affecte pas les tables existantes."""
    metadata.create_all(engine)
