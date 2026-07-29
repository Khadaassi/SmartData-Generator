from typing import Literal

from pydantic import BaseModel

RuleType = Literal["range", "allowed_values", "unique", "date_order"]
RuleSeverity = Literal["blocking", "warning"]


class BusinessRule(BaseModel):
    """Règle métier codée et déterministe (cf. functional_technical_scope.md section 12.7).

    Distincte de la documentation libre indexée dans le RAG : une règle "critique" doit
    être convertie sous cette forme structurée pour être vérifiable de façon fiable
    (cf. user_cases.md section 11 "Format attendu des règles métier").
    """

    id: str
    name: str
    type: RuleType
    field: str
    severity: RuleSeverity = "blocking"
    description: str | None = None

    # type="range"
    min_value: float | None = None
    max_value: float | None = None
    exclusive_min: bool = False
    exclusive_max: bool = False

    # type="allowed_values"
    allowed_values: list[str] | None = None

    # type="date_order" : `field` doit être postérieur ou égal à `compare_field`
    compare_field: str | None = None
