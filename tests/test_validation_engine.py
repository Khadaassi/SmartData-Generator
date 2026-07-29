from domain.rules import BusinessRule
from domain.schema import EntitySpec, FieldSpec
from validation.engine import validate_batch

_ALLOWED_STATUSES = ["EN_ATTENTE", "CONFIRMEE", "EXPEDIEE", "LIVREE", "ANNULEE"]


def _commande_entity() -> EntitySpec:
    return EntitySpec(
        name="Commande",
        fields=[
            FieldSpec(name="reference", type="string"),
            FieldSpec(name="montant_total", type="float"),
            FieldSpec(name="statut", type="string"),
            FieldSpec(name="date_commande", type="date"),
            FieldSpec(name="date_livraison", type="date"),
        ],
    )


def _commande_rules() -> list[BusinessRule]:
    # Reprend les règles de rag/corpus/examples/regles_commande.md sous forme structurée.
    return [
        BusinessRule(
            id="montant-positif",
            name="Montant total positif",
            type="range",
            field="montant_total",
            min_value=0,
            exclusive_min=True,
        ),
        BusinessRule(
            id="statut-valide",
            name="Statut de commande",
            type="allowed_values",
            field="statut",
            allowed_values=_ALLOWED_STATUSES,
        ),
        BusinessRule(
            id="reference-unique",
            name="Unicité de la référence",
            type="unique",
            field="reference",
        ),
        BusinessRule(
            id="dates-coherentes",
            name="Cohérence des dates",
            type="date_order",
            field="date_livraison",
            compare_field="date_commande",
        ),
    ]


def _valid_item(**overrides) -> dict:
    item = {
        "reference": "CMD001",
        "montant_total": 100.0,
        "statut": "CONFIRMEE",
        "date_commande": "2026-01-01",
        "date_livraison": "2026-01-10",
    }
    item.update(overrides)
    return item


def test_validate_batch_accepts_fully_valid_items():
    report = validate_batch(_commande_entity(), [_valid_item()], _commande_rules())

    assert report.status == "PASSED"
    assert report.valid_items == 1
    assert report.rejected_items == 0
    assert report.issues == []
    assert report.valid_data == [_valid_item()]


def test_type_error_is_detected_and_explicit():
    items = [_valid_item(montant_total="pas un nombre")]

    report = validate_batch(_commande_entity(), items, _commande_rules())

    assert report.status == "FAILED"
    assert report.valid_items == 0
    issue = report.issues[0]
    assert issue.level == "error"
    assert issue.code == "type_error"
    assert issue.field == "montant_total"
    assert issue.item_index == 0


def test_range_rule_rejects_non_positive_amount():
    items = [_valid_item(reference="CMD001", montant_total=0), _valid_item(reference="CMD002")]

    report = validate_batch(_commande_entity(), items, _commande_rules())

    assert report.status == "PARTIAL"
    assert report.valid_items == 1
    assert report.rejected_items == 1
    violation = next(issue for issue in report.issues if issue.rule_id == "montant-positif")
    assert violation.level == "error"
    assert violation.item_index == 0
    assert "montant_total=0" in violation.message


def test_allowed_values_rule_rejects_unknown_status():
    items = [_valid_item(statut="INCONNU")]

    report = validate_batch(_commande_entity(), items, _commande_rules())

    assert report.status == "FAILED"
    violation = next(issue for issue in report.issues if issue.rule_id == "statut-valide")
    assert violation.level == "error"
    assert "INCONNU" in violation.message


def test_unique_rule_flags_duplicate_reference():
    items = [_valid_item(reference="CMD001"), _valid_item(reference="CMD001")]

    report = validate_batch(_commande_entity(), items, _commande_rules())

    assert report.status == "PARTIAL"
    assert report.valid_items == 1
    violation = next(issue for issue in report.issues if issue.rule_id == "reference-unique")
    assert violation.item_index == 1
    assert "dupliqué" in violation.message


def test_date_order_rule_rejects_inverted_dates():
    items = [_valid_item(date_commande="2026-05-01", date_livraison="2026-04-01")]

    report = validate_batch(_commande_entity(), items, _commande_rules())

    assert report.status == "FAILED"
    violation = next(issue for issue in report.issues if issue.rule_id == "dates-coherentes")
    assert violation.level == "error"


def test_date_order_rule_rejects_invalid_date_format():
    items = [_valid_item(date_commande="pas-une-date")]

    report = validate_batch(_commande_entity(), items, _commande_rules())

    violation = next(issue for issue in report.issues if issue.code == "date_format_error")
    assert violation.level == "error"


def test_warning_severity_rule_does_not_reject_the_item():
    warning_rule = BusinessRule(
        id="montant-conseille",
        name="Montant conseillé",
        type="range",
        field="montant_total",
        max_value=10_000,
        severity="warning",
    )
    items = [_valid_item(montant_total=50_000)]

    report = validate_batch(_commande_entity(), items, [warning_rule])

    assert report.status == "PASSED_WITH_WARNINGS"
    assert report.valid_items == 1
    assert report.issues[0].level == "warning"


def test_validate_batch_report_mixes_valid_and_rejected_items():
    items = [
        _valid_item(reference="CMD001"),  # valide
        _valid_item(reference="CMD002", montant_total=-10),  # montant invalide
        _valid_item(reference="CMD003", statut="INCONNU"),  # statut invalide
        _valid_item(reference="CMD001"),  # doublon de référence
        _valid_item(reference="CMD005", date_commande="2026-06-01", date_livraison="2026-01-01"),  # dates inversées
    ]

    report = validate_batch(_commande_entity(), items, _commande_rules())

    assert report.total_items == 5
    assert report.valid_items == 1
    assert report.rejected_items == 4
    assert report.status == "PARTIAL"
    assert report.valid_data == [items[0]]
    assert len(report.issues) >= 4
