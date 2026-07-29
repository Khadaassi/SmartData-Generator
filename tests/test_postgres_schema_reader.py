import pytest

from connectors.postgres import (
    ColumnSchema,
    ForeignKeySchema,
    SchemaReaderError,
    TableSchema,
)
from connectors.postgres.schema_reader import compute_generation_order


def _table(name: str, *, foreign_keys: list[ForeignKeySchema] | None = None) -> TableSchema:
    return TableSchema(
        name=name,
        columns=[ColumnSchema(name="id", data_type="integer", nullable=False, is_primary_key=True)],
        primary_key=["id"],
        foreign_keys=foreign_keys or [],
    )


def _fk(referred_table: str, *, column: str = "ref_id") -> ForeignKeySchema:
    return ForeignKeySchema(
        constraint_name=f"fk_{referred_table}", columns=[column], referred_table=referred_table, referred_columns=["id"]
    )


def test_compute_generation_order_respects_foreign_key_dependencies():
    clients = _table("clients")
    commandes = _table("commandes", foreign_keys=[_fk("clients", column="client_id")])

    order = compute_generation_order([commandes, clients])

    assert order.index("clients") < order.index("commandes")


def test_compute_generation_order_handles_independent_tables():
    order = compute_generation_order([_table("a"), _table("b")])

    assert set(order) == {"a", "b"}


def test_compute_generation_order_ignores_self_referencing_foreign_keys():
    employees = _table("employees", foreign_keys=[_fk("employees", column="manager_id")])

    order = compute_generation_order([employees])

    assert order == ["employees"]


def test_compute_generation_order_respects_multi_level_dependencies():
    a = _table("a")
    b = _table("b", foreign_keys=[_fk("a")])
    c = _table("c", foreign_keys=[_fk("b")])

    order = compute_generation_order([c, a, b])

    assert order.index("a") < order.index("b") < order.index("c")


def test_compute_generation_order_detects_circular_dependency():
    a = _table("a", foreign_keys=[_fk("b")])
    b = _table("b", foreign_keys=[_fk("a")])

    with pytest.raises(SchemaReaderError) as exc_info:
        compute_generation_order([a, b])

    assert exc_info.value.code == "circular_dependency"
