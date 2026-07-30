import streamlit as st


def render_execution_summary(result: dict, duration_seconds: float | None = None) -> None:
    generation = result.get("generation", {})
    validation_report = generation.get("validation_report") or {}
    items = generation.get("items", [])
    issues = validation_report.get("issues", [])

    st.subheader("Résumé de l'exécution")

    top = st.columns(4)
    top[0].metric("Statut exécution", result.get("status", "—"))
    top[1].metric("Statut génération", generation.get("status", "—"))
    top[2].metric("Run ID", result.get("run_id", "—"))
    top[3].metric("Durée", f"{duration_seconds:.1f} s" if duration_seconds is not None else "—")

    bottom = st.columns(4)
    bottom[0].metric("Généré", validation_report.get("total_items", len(items)))
    bottom[1].metric("Valides", validation_report.get("valid_items", len(items)))
    bottom[2].metric("Rejetés", validation_report.get("rejected_items", 0))
    bottom[3].metric("Avertissements", sum(1 for issue in issues if issue.get("level") == "warning"))

    if result.get("export_path"):
        st.info(f"Fichier exporté : `{result['export_path']}`")

    if result.get("insert_report"):
        report = result["insert_report"]
        st.success(
            f"{report['rows_inserted']}/{report['rows_attempted']} ligne(s) insérée(s) "
            f"dans `{report['table']}`."
        )

    if generation.get("rules_used"):
        st.caption("Règles RAG utilisées : " + ", ".join(generation["rules_used"]))

    for error in generation.get("errors", []):
        notify = st.error if error.get("blocking", True) else st.warning
        notify(f"[{error.get('stage')}] {error.get('code')} : {error.get('message')}")
