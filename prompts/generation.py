from domain.generation import GenerationRequest
from rag.vectorstore import SearchResult

_SYSTEM_PROMPT = """Tu es un moteur de génération de données métier synthétiques.
Génère des objets réalistes, cohérents entre eux et strictement conformes au schéma fourni.
N'invente jamais de champ absent du schéma. Respecte scrupuleusement les règles métier données en contexte :
en cas de conflit entre ta connaissance générale et une règle métier fournie, la règle métier prévaut toujours."""


def build_generation_prompt(request: GenerationRequest, context: list[SearchResult]) -> list[tuple[str, str]]:
    entity = request.entity
    fields_description = "\n".join(
        f"- {field.name} ({field.type}{'obligatoire' if field.required else 'optionnel'})"
        + (f" : {field.description}" if field.description else "")
        for field in entity.fields
    )

    if context:
        rules_description = "\n".join(f"- {result.text}" for result in context)
    else:
        rules_description = "Aucune règle métier trouvée pour ce contexte : génère des valeurs plausibles génériques."

    human_prompt = f"""Entité à générer : {entity.name}
Nombre d'objets attendus : {request.count}

Champs du schéma :
{fields_description}

Règles métier applicables :
{rules_description}

Génère exactement {request.count} objets "{entity.name}" cohérents entre eux et respectant les règles ci-dessus."""

    return [("system", _SYSTEM_PROMPT), ("human", human_prompt)]
