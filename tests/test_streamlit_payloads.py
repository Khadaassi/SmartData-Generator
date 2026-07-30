from streamlit_app.payloads import (
    build_entity_spec_payload,
    build_generation_payload,
    map_sql_type,
)


def test_map_sql_type_integer_variants():
    assert map_sql_type("integer") == "integer"
    assert map_sql_type("bigint") == "integer"
    assert map_sql_type("SERIAL") == "integer"


def test_map_sql_type_float_variants():
    assert map_sql_type("numeric(10,2)") == "float"
    assert map_sql_type("double precision") == "float"
    assert map_sql_type("real") == "float"


def test_map_sql_type_boolean():
    assert map_sql_type("boolean") == "boolean"


def test_map_sql_type_date_and_datetime():
    assert map_sql_type("date") == "date"
    assert map_sql_type("timestamp without time zone") == "datetime"
    assert map_sql_type("timestamp with time zone") == "datetime"


def test_map_sql_type_defaults_to_string():
    assert map_sql_type("character varying(255)") == "string"
    assert map_sql_type("text") == "string"
    assert map_sql_type("uuid") == "string"


def test_build_entity_spec_payload_marks_not_null_without_default_as_required():
    table = {
        "name": "produits",
        "columns": [
            {"name": "id", "data_type": "integer", "nullable": False, "default": "nextval('produits_id_seq')"},
            {"name": "nom", "data_type": "character varying(255)", "nullable": False, "default": None},
            {"name": "description", "data_type": "text", "nullable": True, "default": None},
        ],
    }

    entity = build_entity_spec_payload(table)

    assert entity["name"] == "produits"
    fields_by_name = {f["name"]: f for f in entity["fields"]}
    assert fields_by_name["id"]["required"] is False
    assert fields_by_name["nom"]["required"] is True
    assert fields_by_name["nom"]["type"] == "string"
    assert fields_by_name["description"]["required"] is False


def test_build_generation_payload_preview_omits_export_and_insert_fields():
    payload = build_generation_payload(
        project_id="proj-1",
        entity={"name": "Produit", "fields": []},
        count=5,
        context_query=None,
        mode="PREVIEW",
    )

    assert payload["mode"] == "PREVIEW"
    assert "export_format" not in payload
    assert "insert_target" not in payload
    assert "confirm_insert" not in payload
    assert payload["generation"]["count"] == 5


def test_build_generation_payload_export_includes_export_format():
    payload = build_generation_payload(
        project_id="proj-1",
        entity={"name": "Produit", "fields": []},
        count=5,
        context_query=None,
        mode="EXPORT",
        export_format="csv",
    )

    assert payload["export_format"] == "csv"
    assert "insert_target" not in payload


def test_build_generation_payload_insert_includes_target_and_confirmation():
    insert_target = {"database_url": "postgresql+psycopg://u:p@localhost/db", "table": "produits", "schema_name": "public"}

    payload = build_generation_payload(
        project_id="proj-1",
        entity={"name": "Produit", "fields": []},
        count=5,
        context_query="contexte",
        mode="INSERT",
        insert_target=insert_target,
        confirm_insert=True,
    )

    assert payload["insert_target"] == insert_target
    assert payload["confirm_insert"] is True
    assert payload["generation"]["context_query"] == "contexte"


def test_build_generation_payload_blank_context_query_becomes_none():
    payload = build_generation_payload(
        project_id="proj-1",
        entity={"name": "Produit", "fields": []},
        count=1,
        context_query="",
        mode="PREVIEW",
    )

    assert payload["generation"]["context_query"] is None
