from sqlalchemy import MetaData, Table
from sqlalchemy import insert as sa_insert
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from connectors.postgres.errors import DataWriteError


def insert_records(
    database_url: str, *, schema: str, table: str, items: list[dict], engine: Engine | None = None
) -> int:
    """Insère des enregistrements dans une table PostgreSQL au sein d'une transaction unique.

    Utilise l'API Core de SQLAlchemy (requêtes paramétrées) : le SQL n'est jamais
    construit à partir d'une chaîne assemblée dynamiquement, conformément à
    l'interdiction du SQL généré librement par le LLM (cf. technical_architecture.md
    section 6.26 et 15). Toute erreur entraîne un rollback complet — aucune écriture partielle.
    """
    if not items:
        raise DataWriteError(code="no_data", message="Aucun enregistrement à insérer.")

    owns_engine = engine is None
    db_engine = engine or create_engine(database_url)

    try:
        try:
            target_table = Table(table, MetaData(), schema=schema, autoload_with=db_engine)
        except SQLAlchemyError as exc:
            raise DataWriteError(
                code="table_not_found", message=f"Table '{schema}.{table}' introuvable : {exc}"
            ) from exc

        known_columns = set(target_table.columns.keys())
        for index, item in enumerate(items):
            unknown = set(item) - known_columns
            if unknown:
                raise DataWriteError(
                    code="unknown_column",
                    message=f"Colonne(s) inconnue(s) {sorted(unknown)} pour l'objet {index} de la table '{table}'.",
                )

        try:
            with db_engine.begin() as conn:
                conn.execute(sa_insert(target_table), items)
        except OperationalError as exc:
            raise DataWriteError(code="connection_error", message=f"Connexion PostgreSQL impossible : {exc}") from exc
        except IntegrityError as exc:
            raise DataWriteError(
                code="integrity_error", message=f"Contrainte violée lors de l'insertion dans '{table}' : {exc}"
            ) from exc
        except SQLAlchemyError as exc:
            raise DataWriteError(
                code="insert_error", message=f"Erreur lors de l'insertion dans '{table}' : {exc}"
            ) from exc
    finally:
        if owns_engine:
            db_engine.dispose()

    return len(items)
