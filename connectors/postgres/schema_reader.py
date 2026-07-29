from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine, Inspector
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from connectors.postgres.errors import SchemaReaderError
from connectors.postgres.schema import (
    CheckConstraintSchema,
    ColumnSchema,
    DatabaseSchema,
    ForeignKeySchema,
    TableSchema,
    UniqueConstraintSchema,
)


def test_connection(database_url: str) -> bool:
    """Vérifie qu'une connexion PostgreSQL peut être établie avec l'URL fournie."""
    engine = create_engine(database_url)
    try:
        with engine.connect():
            return True
    except OperationalError as exc:
        raise SchemaReaderError(code="connection_error", message=f"Connexion PostgreSQL impossible : {exc}") from exc
    finally:
        engine.dispose()


def read_schema(database_url: str, *, schema: str = "public", engine: Engine | None = None) -> DatabaseSchema:
    """Inspecte une base PostgreSQL et retourne une représentation normalisée du schéma.

    L'analyse est déterministe : elle lit les métadonnées exposées par PostgreSQL
    via SQLAlchemy sans jamais inventer une structure absente (cf.
    technical_architecture.md section 6.8, "le Schema Analyzer constitue la
    source de vérité technique").
    """
    owns_engine = engine is None
    db_engine = engine

    try:
        db_engine = db_engine or create_engine(database_url)
        inspector = inspect(db_engine)
        table_names = inspector.get_table_names(schema=schema)

        if not table_names:
            raise SchemaReaderError(code="empty_schema", message=f"Aucune table trouvée dans le schéma '{schema}'.")

        tables = [_read_table(inspector, name, schema) for name in table_names]
    except OperationalError as exc:
        raise SchemaReaderError(code="connection_error", message=f"Connexion PostgreSQL impossible : {exc}") from exc
    except SQLAlchemyError as exc:
        raise SchemaReaderError(
            code="introspection_error", message=f"Erreur lors de l'inspection du schéma : {exc}"
        ) from exc
    finally:
        if owns_engine and db_engine is not None:
            db_engine.dispose()

    return DatabaseSchema(schema_name=schema, tables=tables, generation_order=compute_generation_order(tables))


def _read_table(inspector: Inspector, table_name: str, schema: str) -> TableSchema:
    pk_info = inspector.get_pk_constraint(table_name, schema=schema)
    primary_key = list(pk_info.get("constrained_columns") or [])
    pk_columns = set(primary_key)

    unique_constraints = [
        UniqueConstraintSchema(
            constraint_name=uc.get("name") or f"{table_name}_unique_{index}",
            columns=list(uc["column_names"]),
        )
        for index, uc in enumerate(inspector.get_unique_constraints(table_name, schema=schema))
    ]
    unique_columns = {uc.columns[0] for uc in unique_constraints if len(uc.columns) == 1}

    columns = [_build_column(col, pk_columns, unique_columns) for col in inspector.get_columns(table_name, schema=schema)]

    foreign_keys = [
        ForeignKeySchema(
            constraint_name=fk.get("name") or f"{table_name}_fk_{index}",
            columns=list(fk["constrained_columns"]),
            referred_table=fk["referred_table"],
            referred_columns=list(fk["referred_columns"]),
        )
        for index, fk in enumerate(inspector.get_foreign_keys(table_name, schema=schema))
    ]

    check_constraints = [
        CheckConstraintSchema(
            constraint_name=cc.get("name") or f"{table_name}_check_{index}",
            sql_text=str(cc["sqltext"]),
        )
        for index, cc in enumerate(inspector.get_check_constraints(table_name, schema=schema))
    ]

    return TableSchema(
        name=table_name,
        columns=columns,
        primary_key=primary_key,
        foreign_keys=foreign_keys,
        unique_constraints=unique_constraints,
        check_constraints=check_constraints,
    )


def _build_column(col: dict, pk_columns: set[str], unique_columns: set[str]) -> ColumnSchema:
    default = col.get("default")
    return ColumnSchema(
        name=col["name"],
        data_type=str(col["type"]),
        nullable=bool(col.get("nullable", True)),
        default=str(default) if default is not None else None,
        is_primary_key=col["name"] in pk_columns,
        is_unique=col["name"] in unique_columns,
    )


def compute_generation_order(tables: list[TableSchema]) -> list[str]:
    """Ordonne les tables pour qu'une table n'apparaisse qu'après celles qu'elle référence.

    Les auto-références (une table qui pointe vers elle-même, ex. `employees.manager_id`)
    ne constituent pas une dépendance d'ordre et sont ignorées. Une dépendance circulaire
    entre plusieurs tables ne peut en revanche pas être ordonnée : elle est signalée.
    """
    table_names = {table.name for table in tables}
    dependencies: dict[str, set[str]] = {table.name: set() for table in tables}
    for table in tables:
        for fk in table.foreign_keys:
            if fk.referred_table != table.name and fk.referred_table in table_names:
                dependencies[table.name].add(fk.referred_table)

    ordered: list[str] = []
    remaining = dependencies
    while remaining:
        ready = sorted(name for name, deps in remaining.items() if not deps)
        if not ready:
            raise SchemaReaderError(
                code="circular_dependency",
                message=f"Dépendance circulaire détectée entre les tables : {sorted(remaining)}.",
            )

        for name in ready:
            del remaining[name]
        for deps in remaining.values():
            deps.difference_update(ready)

        ordered.extend(ready)

    return ordered
