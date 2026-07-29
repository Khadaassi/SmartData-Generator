import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from connectors.postgres import SchemaReaderError, read_schema
from connectors.postgres import test_connection as pg_test_connection
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
    name = f"t13_{uuid.uuid4().hex[:8]}"
    engine = create_engine(settings.database_url)
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{name}"'))
        conn.execute(
            text(
                f"""
                CREATE TABLE "{name}".clients (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE
                )
                """
            )
        )
        conn.execute(
            text(
                f"""
                CREATE TABLE "{name}".commandes (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER NOT NULL REFERENCES "{name}".clients(id),
                    montant NUMERIC NOT NULL CHECK (montant > 0)
                )
                """
            )
        )

    yield name

    with engine.begin() as conn:
        conn.execute(text(f'DROP SCHEMA "{name}" CASCADE'))
    engine.dispose()


def test_connection_succeeds_with_a_valid_url():
    assert pg_test_connection(settings.database_url) is True


def test_connection_raises_data_reader_error_for_an_unreachable_host():
    bad_url = "postgresql+psycopg://smartdata:smartdata@localhost:59999/smartdata_generator"

    with pytest.raises(SchemaReaderError) as exc_info:
        pg_test_connection(bad_url)

    assert exc_info.value.code == "connection_error"


def test_read_schema_detects_tables_and_columns(schema_name):
    result = read_schema(settings.database_url, schema=schema_name)

    assert {table.name for table in result.tables} == {"clients", "commandes"}


def test_read_schema_detects_primary_keys(schema_name):
    result = read_schema(settings.database_url, schema=schema_name)

    clients = next(table for table in result.tables if table.name == "clients")
    assert clients.primary_key == ["id"]


def test_read_schema_detects_foreign_keys(schema_name):
    result = read_schema(settings.database_url, schema=schema_name)

    commandes = next(table for table in result.tables if table.name == "commandes")
    assert len(commandes.foreign_keys) == 1
    fk = commandes.foreign_keys[0]
    assert fk.columns == ["client_id"]
    assert fk.referred_table == "clients"
    assert fk.referred_columns == ["id"]


def test_read_schema_detects_unique_and_check_constraints(schema_name):
    result = read_schema(settings.database_url, schema=schema_name)

    clients = next(table for table in result.tables if table.name == "clients")
    email_column = next(col for col in clients.columns if col.name == "email")
    assert email_column.is_unique is True

    commandes = next(table for table in result.tables if table.name == "commandes")
    assert len(commandes.check_constraints) == 1


def test_read_schema_orders_tables_respecting_dependencies(schema_name):
    result = read_schema(settings.database_url, schema=schema_name)

    assert result.generation_order.index("clients") < result.generation_order.index("commandes")


def test_read_schema_empty_schema_raises_schema_reader_error():
    empty_schema = f"t13_empty_{uuid.uuid4().hex[:8]}"
    engine = create_engine(settings.database_url)
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{empty_schema}"'))

    try:
        with pytest.raises(SchemaReaderError) as exc_info:
            read_schema(settings.database_url, schema=empty_schema)
        assert exc_info.value.code == "empty_schema"
    finally:
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{empty_schema}" CASCADE'))
        engine.dispose()
