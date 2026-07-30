# Le Schema Analyzer expose le type SQL brut (ex. "character varying(255)") : cette
# table de correspondance le convertit vers le FieldType générique attendu par le
# contrat EntitySpec de l'API, aucune conversion de ce type n'existe côté service.
_TYPE_KEYWORDS: list[tuple[str, str]] = [
    ("bool", "boolean"),
    ("timestamp", "datetime"),
    ("date", "date"),
    ("time", "datetime"),
    ("numeric", "float"),
    ("decimal", "float"),
    ("real", "float"),
    ("double", "float"),
    ("float", "float"),
    ("int", "integer"),
    ("serial", "integer"),
]


def map_sql_type(data_type: str) -> str:
    normalized = data_type.lower()
    for keyword, field_type in _TYPE_KEYWORDS:
        if keyword in normalized:
            return field_type
    return "string"


def build_entity_spec_payload(table: dict) -> dict:
    """Construit un EntitySpec (contrat API) à partir d'une table renvoyée par
    `POST /schema/postgres`. Une colonne dotée d'une valeur par défaut n'est pas
    considérée comme obligatoire, même si elle est NOT NULL en base."""
    fields = [
        {
            "name": column["name"],
            "type": map_sql_type(column["data_type"]),
            "required": (not column["nullable"]) and column.get("default") is None,
        }
        for column in table["columns"]
    ]
    return {"name": table["name"], "fields": fields}


def build_generation_payload(
    *,
    project_id: str,
    entity: dict,
    count: int,
    context_query: str | None,
    mode: str,
    export_format: str = "json",
    insert_target: dict | None = None,
    confirm_insert: bool = False,
) -> dict:
    """Construit le payload de `POST /executions` à partir du contrat ExecutionRequest.

    Preview est toujours le mode par défaut à l'appel ; export_format n'est inclus
    qu'en mode EXPORT et insert_target/confirm_insert qu'en mode INSERT, pour ne
    jamais laisser croire qu'une confirmation a été donnée hors de ce mode.
    """
    payload: dict = {
        "generation": {
            "project_id": project_id,
            "entity": entity,
            "count": count,
            "context_query": context_query or None,
        },
        "mode": mode,
    }
    if mode == "EXPORT":
        payload["export_format"] = export_format
    if mode == "INSERT":
        payload["insert_target"] = insert_target
        payload["confirm_insert"] = confirm_insert
    return payload
