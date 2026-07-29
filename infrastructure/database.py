from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from infrastructure.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Moteur SQLAlchemy vers le stockage interne de SmartData Generator.

    Distinct des connecteurs PostgreSQL (connectors/postgres), qui ciblent toujours
    une base cible fournie explicitement par l'appelant : cette base-ci est la
    base applicative du service lui-même (cf. technical_architecture.md section 6.30).
    """
    return create_engine(get_settings().database_url)
