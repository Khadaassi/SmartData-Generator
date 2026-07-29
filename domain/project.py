from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from domain.rules import BusinessRule
from domain.schema import EntitySpec

ConnectorType = Literal["csv", "json", "rest", "postgres"]


class GenerationParameters(BaseModel):
    """Paramètres de génération par défaut d'un projet.

    Une exécution (`GenerationRequest`) peut toujours les surcharger explicitement ;
    la borne finale (`count`) reste appliquée à ce niveau-là, pas ici."""

    default_count: int = Field(default=10, gt=0)
    llm_provider: str | None = None
    llm_model: str | None = None


class ConnectorConfig(BaseModel):
    """Référence à une source ou une destination configurée pour le projet.

    Le type détermine quel connecteur sera sélectionné ; la forme précise de `config`
    dépend de ce type (ex. `database_url`/`table` pour "postgres", `path` pour "csv"/"json")
    et est revalidée par le connecteur concerné au moment de son utilisation
    (cf. technical_architecture.md section 10.2 : aucune logique connecteur ici)."""

    type: ConnectorType
    config: dict[str, Any] = Field(default_factory=dict)


class ProjectConfig(BaseModel):
    """Configuration complète d'un projet de génération : ce qui rend SmartData Generator
    réutilisable d'un contexte métier à l'autre sans modifier son cœur
    (cf. functional_technical_scope.md section 1 et 12.4)."""

    entities: list[EntitySpec] = Field(default_factory=list)
    rules: list[BusinessRule] = Field(default_factory=list)
    generation_parameters: GenerationParameters = Field(default_factory=GenerationParameters)
    source: ConnectorConfig | None = None
    destination: ConnectorConfig | None = None

    @model_validator(mode="after")
    def _check_unique_entity_names(self) -> "ProjectConfig":
        names = [entity.name for entity in self.entities]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            raise ValueError(f"Noms d'entité en doublon dans la configuration du projet : {sorted(duplicates)}.")
        return self


class Project(BaseModel):
    """Un projet représente un contexte de génération indépendant : il ne contient
    aucune logique métier codée, seulement de la configuration (cf.
    functional_technical_scope.md section 6.1)."""

    id: str
    name: str = Field(min_length=1)
    description: str | None = None
    config: ProjectConfig = Field(default_factory=ProjectConfig)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
