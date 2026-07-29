import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from connectors.postgres import DataWriteError, insert_records
from infrastructure.config import get_settings
from tests.integration._reachability import is_reachable

settings = get_settings()
_db_url = make_url(settings.database_url)

pytestmark = pytest.mark.skipif(
    not is_reachable(_db_url.host, _db_url.port or 5432),
    reason="PostgreSQL non accessible (docker compose -f docker/docker-compose.yml up -d postgres)",
)


@pytest.fixture
def schema_name():
    name = f"t14_{uuid.uuid4().hex[:8]}"
    engine = create_engine(settings.database_url)
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{name}"'))
        conn.execute(
            text(
                f"""
                CREATE TABLE "{name}".produits (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    prix NUMERIC NOT NULL CHECK (prix > 0)
                )
                """
            )
        )

    yield name

    with engine.begin() as conn:
        conn.execute(text(f'DROP SCHEMA "{name}" CASCADE'))
    engine.dispose()


def _count_rows(schema_name: str, table: str = "produits") -> int:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        count = conn.execute(text(f'SELECT count(*) FROM "{schema_name}"."{table}"')).scalar_one()
    engine.dispose()
    return count


def test_insert_records_inserts_all_rows(schema_name):
    items = [{"nom": "Clavier", "prix": 29.9}, {"nom": "Souris", "prix": 15.0}]

    rows_inserted = insert_records(settings.database_url, schema=schema_name, table="produits", items=items)

    assert rows_inserted == 2
    assert _count_rows(schema_name) == 2


def test_insert_records_rolls_back_entirely_on_constraint_violation(schema_name):
    items = [{"nom": "Clavier", "prix": 29.9}, {"nom": "Souris", "prix": -5.0}]  # viole le CHECK (prix > 0)

    with pytest.raises(DataWriteError) as exc_info:
        insert_records(settings.database_url, schema=schema_name, table="produits", items=items)

    assert exc_info.value.code == "integrity_error"
    assert _count_rows(schema_name) == 0  # transaction unique : rien n'a été inséré


def test_insert_records_rejects_unknown_column(schema_name):
    items = [{"nom": "Clavier", "prix": 29.9, "couleur": "noir"}]

    with pytest.raises(DataWriteError) as exc_info:
        insert_records(settings.database_url, schema=schema_name, table="produits", items=items)

    assert exc_info.value.code == "unknown_column"
    assert _count_rows(schema_name) == 0


def test_insert_records_table_not_found_raises_data_write_error(schema_name):
    with pytest.raises(DataWriteError) as exc_info:
        insert_records(settings.database_url, schema=schema_name, table="does_not_exist", items=[{"a": 1}])

    assert exc_info.value.code == "table_not_found"


def test_insert_records_empty_items_raises_data_write_error(schema_name):
    with pytest.raises(DataWriteError) as exc_info:
        insert_records(settings.database_url, schema=schema_name, table="produits", items=[])

    assert exc_info.value.code == "no_data"
