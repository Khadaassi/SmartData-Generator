import streamlit as st

_STATUS_ICON = {
    "PASSED": "✅",
    "PASSED_WITH_WARNINGS": "⚠️",
    "PARTIAL": "🟠",
    "FAILED": "❌",
}


def render_validation_report(result: dict) -> None:
    report = (result.get("generation") or {}).get("validation_report")

    st.subheader("Rapport de validation")
    if not report:
        st.info("Aucun rapport de validation disponible pour cette exécution.")
        return

    status = report.get("status", "—")
    st.write(f"{_STATUS_ICON.get(status, '')} **Statut** : {status}")

    cols = st.columns(3)
    cols[0].metric("Total", report.get("total_items", 0))
    cols[1].metric("Valides", report.get("valid_items", 0))
    cols[2].metric("Rejetés", report.get("rejected_items", 0))

    issues = report.get("issues", [])
    if not issues:
        st.success("Aucun problème signalé.")
        return

    for issue in issues:
        message = (
            f"[{issue.get('rule_id') or issue.get('code')}] {issue.get('message')} "
            f"(champ : {issue.get('field') or '—'}, item : {issue.get('item_index')})"
        )
        (st.error if issue.get("level") == "error" else st.warning)(message)

    with st.expander("Diagnostic (lecture seule)"):
        st.caption(
            "Informations fournies à titre diagnostique uniquement : les données "
            "rejetées ne sont jamais proposées à l'export ou à l'insertion."
        )
        st.json(issues)
