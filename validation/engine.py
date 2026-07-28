from datetime import date

from pydantic import ValidationError

from domain.rules import BusinessRule
from domain.schema import EntitySpec, build_entity_model
from validation.schemas import IssueLevel, ValidationIssue, ValidationReport


def _validate_types(entity: EntitySpec, items: list[dict]) -> tuple[dict[int, dict], list[ValidationIssue]]:
    """Revalide chaque objet contre le modèle Pydantic de l'entité (types, champs obligatoires)."""
    model = build_entity_model(entity)
    valid: dict[int, dict] = {}
    issues: list[ValidationIssue] = []

    for index, raw_item in enumerate(items):
        try:
            validated = model.model_validate(raw_item)
        except ValidationError as exc:
            for error in exc.errors():
                field = ".".join(str(part) for part in error["loc"]) or None
                issues.append(
                    ValidationIssue(
                        level=IssueLevel.ERROR,
                        code="type_error",
                        message=error["msg"],
                        item_index=index,
                        field=field,
                    )
                )
        else:
            valid[index] = validated.model_dump()

    return valid, issues


def _issue(
    rule: BusinessRule,
    index: int,
    message: str,
    *,
    code: str = "business_rule_violation",
    level: IssueLevel | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        level=level or (IssueLevel.ERROR if rule.severity == "blocking" else IssueLevel.WARNING),
        code=code,
        message=message,
        item_index=index,
        field=rule.field,
        rule_id=rule.id,
    )


def _check_range(rule: BusinessRule, index: int, item: dict) -> ValidationIssue | None:
    value = item.get(rule.field)
    if value is None:
        return None

    if rule.min_value is not None:
        if rule.exclusive_min and value <= rule.min_value:
            return _issue(rule, index, f"{rule.field}={value} doit être strictement supérieur à {rule.min_value}.")
        if not rule.exclusive_min and value < rule.min_value:
            return _issue(rule, index, f"{rule.field}={value} doit être supérieur ou égal à {rule.min_value}.")

    if rule.max_value is not None:
        if rule.exclusive_max and value >= rule.max_value:
            return _issue(rule, index, f"{rule.field}={value} doit être strictement inférieur à {rule.max_value}.")
        if not rule.exclusive_max and value > rule.max_value:
            return _issue(rule, index, f"{rule.field}={value} doit être inférieur ou égal à {rule.max_value}.")

    return None


def _check_allowed_values(rule: BusinessRule, index: int, item: dict) -> ValidationIssue | None:
    value = item.get(rule.field)
    if value is None or not rule.allowed_values:
        return None
    if value not in rule.allowed_values:
        return _issue(
            rule, index, f"{rule.field}={value!r} n'appartient pas aux valeurs autorisées {rule.allowed_values}."
        )
    return None


def _check_date_order(rule: BusinessRule, index: int, item: dict) -> ValidationIssue | None:
    if not rule.compare_field:
        return None

    field_value = item.get(rule.field)
    compare_value = item.get(rule.compare_field)
    if field_value is None or compare_value is None:
        return None

    try:
        field_date = date.fromisoformat(str(field_value))
        compare_date = date.fromisoformat(str(compare_value))
    except ValueError:
        return _issue(
            rule,
            index,
            f"{rule.field} ou {rule.compare_field} n'est pas une date ISO 8601 valide.",
            code="date_format_error",
            level=IssueLevel.ERROR,
        )

    if field_date < compare_date:
        return _issue(
            rule,
            index,
            f"{rule.field}={field_value} doit être postérieur ou égal à {rule.compare_field}={compare_value}.",
        )

    return None


def _check_unique(rule: BusinessRule, valid_items: dict[int, dict]) -> list[ValidationIssue]:
    seen: dict[object, int] = {}
    issues: list[ValidationIssue] = []

    for index, item in sorted(valid_items.items()):
        value = item.get(rule.field)
        if value is None:
            continue
        if value in seen:
            issues.append(
                _issue(rule, index, f"{rule.field}={value!r} est dupliqué (déjà utilisé par l'objet {seen[value]}).")
            )
        else:
            seen[value] = index

    return issues


def _check_business_rules(rules: list[BusinessRule], valid_items: dict[int, dict]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for rule in rules:
        if rule.type == "unique":
            issues.extend(_check_unique(rule, valid_items))
            continue

        for index, item in valid_items.items():
            issue = None
            if rule.type == "range":
                issue = _check_range(rule, index, item)
            elif rule.type == "allowed_values":
                issue = _check_allowed_values(rule, index, item)
            elif rule.type == "date_order":
                issue = _check_date_order(rule, index, item)

            if issue is not None:
                issues.append(issue)

    return issues


def validate_batch(entity: EntitySpec, items: list[dict], rules: list[BusinessRule] | None = None) -> ValidationReport:
    """Valide un batch généré : types (Pydantic) puis règles métier codées et déterministes.

    Les objets en erreur bloquante sont exclus de `valid_data` ; chaque problème détecté
    (bloquant ou non) est détaillé dans `issues` pour que l'appelant sache exactement pourquoi.
    """
    valid_items, issues = _validate_types(entity, items)
    issues.extend(_check_business_rules(rules or [], valid_items))

    rejected_indexes = {
        issue.item_index for issue in issues if issue.level == IssueLevel.ERROR and issue.item_index is not None
    }
    valid_data = [item for index, item in sorted(valid_items.items()) if index not in rejected_indexes]

    has_errors = any(issue.level == IssueLevel.ERROR for issue in issues)
    has_warnings = any(issue.level == IssueLevel.WARNING for issue in issues)

    if not valid_data:
        status = "FAILED"
    elif has_errors:
        status = "PARTIAL"
    elif has_warnings:
        status = "PASSED_WITH_WARNINGS"
    else:
        status = "PASSED"

    return ValidationReport(
        entity=entity.name,
        total_items=len(items),
        valid_items=len(valid_data),
        rejected_items=len(items) - len(valid_data),
        issues=issues,
        valid_data=valid_data,
        status=status,
    )
