from uuid import uuid4

import streamlit as st

from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError

_RULE_TYPES = ["range", "allowed_values", "unique", "date_order"]


def _base_rule(*, name: str, rule_type: str, field: str, severity: str, description: str | None) -> dict:
    return {
        "id": uuid4().hex,
        "name": name,
        "type": rule_type,
        "field": field,
        "severity": severity,
        "description": description or None,
    }


def build_range_rule(
    *,
    name: str,
    field: str,
    severity: str,
    description: str | None,
    min_value: float | None,
    max_value: float | None,
    exclusive_min: bool,
    exclusive_max: bool,
) -> dict:
    rule = _base_rule(name=name, rule_type="range", field=field, severity=severity, description=description)
    rule.update(
        min_value=min_value, max_value=max_value, exclusive_min=exclusive_min, exclusive_max=exclusive_max
    )
    return rule


def build_allowed_values_rule(
    *, name: str, field: str, severity: str, description: str | None, allowed_values: list[str]
) -> dict:
    rule = _base_rule(name=name, rule_type="allowed_values", field=field, severity=severity, description=description)
    rule["allowed_values"] = allowed_values
    return rule


def build_unique_rule(*, name: str, field: str, severity: str, description: str | None) -> dict:
    return _base_rule(name=name, rule_type="unique", field=field, severity=severity, description=description)


def build_date_order_rule(
    *, name: str, field: str, severity: str, description: str | None, compare_field: str
) -> dict:
    rule = _base_rule(name=name, rule_type="date_order", field=field, severity=severity, description=description)
    rule["compare_field"] = compare_field
    return rule


def render_rule_builder(client: ApiClient, project_id: str) -> None:
    st.subheader("Règles métier")

    try:
        project = client.get_project(project_id)
    except SmartDataGeneratorApiError as exc:
        st.error(exc.message)
        return

    rules: list[dict] = project["config"]["rules"]

    if not rules:
        st.caption("Aucune règle définie pour ce projet.")
    for rule in rules:
        with st.expander(f"{rule['name']} — {rule['type']} ({rule['severity']})"):
            st.json(rule)
            if st.button("Supprimer cette règle", key=f"delete_rule_{project_id}_{rule['id']}"):
                _save_rules(client, project_id, [r for r in rules if r["id"] != rule["id"]])

    st.markdown("**Ajouter une règle**")
    _render_new_rule_form(client, project_id, rules)


def _render_new_rule_form(client: ApiClient, project_id: str, rules: list[dict]) -> None:
    rule_type = st.selectbox("Type de règle", _RULE_TYPES, key=f"new_rule_type_{project_id}")
    name = st.text_input("Nom de la règle", key=f"new_rule_name_{project_id}")
    field = st.text_input("Champ concerné", key=f"new_rule_field_{project_id}")
    severity = st.radio(
        "Sévérité", ["blocking", "warning"], horizontal=True, key=f"new_rule_severity_{project_id}"
    )
    description = st.text_area("Description (optionnel)", key=f"new_rule_description_{project_id}")

    new_rule = _render_type_specific_fields(project_id, rule_type, name, field, severity, description)

    if st.button("Ajouter la règle", disabled=not (name and field), key=f"add_rule_{project_id}"):
        _save_rules(client, project_id, [*rules, new_rule])


def _render_type_specific_fields(
    project_id: str, rule_type: str, name: str, field: str, severity: str, description: str
) -> dict:
    if rule_type == "range":
        min_value = st.number_input("Valeur minimale", value=0.0, key=f"new_rule_min_{project_id}")
        max_value = st.number_input("Valeur maximale", value=100.0, key=f"new_rule_max_{project_id}")
        exclusive_min = st.checkbox("Minimum exclusif", key=f"new_rule_excl_min_{project_id}")
        exclusive_max = st.checkbox("Maximum exclusif", key=f"new_rule_excl_max_{project_id}")
        return build_range_rule(
            name=name,
            field=field,
            severity=severity,
            description=description,
            min_value=min_value,
            max_value=max_value,
            exclusive_min=exclusive_min,
            exclusive_max=exclusive_max,
        )

    if rule_type == "allowed_values":
        raw_values = st.text_input(
            "Valeurs autorisées (séparées par des virgules)", key=f"new_rule_values_{project_id}"
        )
        allowed_values = [value.strip() for value in raw_values.split(",") if value.strip()]
        return build_allowed_values_rule(
            name=name, field=field, severity=severity, description=description, allowed_values=allowed_values
        )

    if rule_type == "date_order":
        compare_field = st.text_input(
            "Champ de comparaison (doit être antérieur ou égal)", key=f"new_rule_compare_{project_id}"
        )
        return build_date_order_rule(
            name=name, field=field, severity=severity, description=description, compare_field=compare_field
        )

    return build_unique_rule(name=name, field=field, severity=severity, description=description)


def _save_rules(client: ApiClient, project_id: str, rules: list[dict]) -> None:
    try:
        client.update_project_rules(project_id, rules)
    except SmartDataGeneratorApiError as exc:
        st.error(exc.message)
    else:
        st.rerun()
