from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    """Colonne telle qu'exposée par PostgreSQL. Le type reste la représentation SQL
    brute (ex. "character varying(255)") : sa conversion vers un type applicatif
    relève du Schema Analyzer, pas du connecteur (cf. technical_architecture.md
    section 6.23, "ne pas inventer les types")."""

    name: str
    data_type: str
    nullable: bool
    default: str | None = None
    is_primary_key: bool = False
    is_unique: bool = False


class ForeignKeySchema(BaseModel):
    constraint_name: str
    columns: list[str]
    referred_table: str
    referred_columns: list[str]


class UniqueConstraintSchema(BaseModel):
    constraint_name: str
    columns: list[str]


class CheckConstraintSchema(BaseModel):
    constraint_name: str
    sql_text: str


class TableSchema(BaseModel):
    name: str
    columns: list[ColumnSchema]
    primary_key: list[str] = Field(default_factory=list)
    foreign_keys: list[ForeignKeySchema] = Field(default_factory=list)
    unique_constraints: list[UniqueConstraintSchema] = Field(default_factory=list)
    check_constraints: list[CheckConstraintSchema] = Field(default_factory=list)


class DatabaseSchema(BaseModel):
    """Représentation normalisée et exploitable du schéma d'une base PostgreSQL.

    `generation_order` respecte les dépendances de clés étrangères entre tables
    (une table n'apparaît qu'après celles qu'elle référence), afin de pouvoir
    piloter directement l'ordre de génération et d'insertion.
    """

    schema_name: str
    tables: list[TableSchema]
    generation_order: list[str]
