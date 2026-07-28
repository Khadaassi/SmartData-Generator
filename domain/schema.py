from typing import Literal

from pydantic import BaseModel, Field, create_model

FieldType = Literal["string", "integer", "float", "boolean", "date", "datetime"]

_PYTHON_TYPES: dict[FieldType, type] = {
    "string": str,
    "integer": int,
    "float": float,
    "boolean": bool,
    "date": str,
    "datetime": str,
}


class FieldSpec(BaseModel):
    name: str
    type: FieldType
    required: bool = True
    description: str | None = None
    allowed_values: list[str] | None = None


class EntitySpec(BaseModel):
    name: str
    fields: list[FieldSpec] = Field(min_length=1)


def build_entity_model(entity: EntitySpec) -> type[BaseModel]:
    """Construit dynamiquement un modèle Pydantic à partir d'une spécification d'entité.

    Le schéma cible n'est pas connu à l'avance (fourni par le client, cf. Schema Analyzer) :
    ce modèle sert de contrat de sortie structurée pour le LLM et de validation de base.
    """
    fields: dict[str, tuple] = {}
    for field in entity.fields:
        python_type = _PYTHON_TYPES[field.type]

        description = field.description or ""
        if field.type in ("date", "datetime"):
            description = f"{description} (format ISO 8601)".strip()
        if field.allowed_values:
            description = f"{description} Valeurs autorisées : {', '.join(field.allowed_values)}.".strip()

        if field.required:
            fields[field.name] = (python_type, Field(description=description or None))
        else:
            fields[field.name] = (python_type | None, Field(default=None, description=description or None))

    return create_model(entity.name, **fields)
