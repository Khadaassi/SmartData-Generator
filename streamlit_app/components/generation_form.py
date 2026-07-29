import time

import streamlit as st

from streamlit_app import state
from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError
from streamlit_app.components.insert_confirmation import render_insert_confirmation
from streamlit_app.payloads import build_entity_spec_payload, build_generation_payload

_MAX_COUNT = 50
_MODE_OPTIONS = {
    "Preview": ("PREVIEW", "json"),
    "Export CSV": ("EXPORT", "csv"),
    "Export JSON": ("EXPORT", "json"),
    "Insert PostgreSQL": ("INSERT", "json"),
}


def render_generation_form(client: ApiClient) -> None:
    schema_result = st.session_state.get(state.SCHEMA_RESULT)
    if not schema_result:
        st.info("Analysez d'abord un schéma PostgreSQL (page Schema) pour sélectionner une entité.")
        return

    tables = schema_result.get("tables", [])
    if not tables:
        st.warning("Aucune table détectée dans le schéma analysé.")
        return

    table = _render_entity_selection(tables)

    st.subheader("Génération")
    st.caption(
        "Les documents indexés et les règles métier du projet (page Project) sont "
        "appliqués automatiquement à la recherche RAG et à la validation."
    )
    project_id = st.session_state.get(state.PROJECT_ID, "")
    count = st.number_input("Nombre d'enregistrements", min_value=1, max_value=_MAX_COUNT, value=5, step=1)
    context_query = st.text_area("Instructions complémentaires (optionnel)", value="")
    mode_label = st.radio("Mode d'exécution", list(_MODE_OPTIONS.keys()), index=0, horizontal=True)
    mode, export_format = _MODE_OPTIONS[mode_label]

    insert_target, confirm_insert = (None, False)
    if mode == "INSERT":
        insert_target, confirm_insert = render_insert_confirmation(default_table=table["name"])

    disabled = mode == "INSERT" and (insert_target is None or not confirm_insert)
    button_label = "Lancer l'insertion" if mode == "INSERT" else "Lancer l'exécution"

    if st.button(button_label, disabled=disabled, type="primary"):
        _run_execution(
            client,
            project_id=project_id,
            table=table,
            count=int(count),
            context_query=context_query,
            mode=mode,
            export_format=export_format,
            insert_target=insert_target,
            confirm_insert=confirm_insert,
        )


def _render_entity_selection(tables: list[dict]) -> dict:
    st.subheader("Sélection de l'entité")
    table_names = [t["name"] for t in tables]
    entity_name = st.selectbox("Entité", table_names, key="entity_select")
    table = next(t for t in tables if t["name"] == entity_name)
    st.session_state[state.SELECTED_ENTITY] = entity_name

    with st.expander("Détail de l'entité", expanded=False):
        st.dataframe(
            [
                {
                    "champ": c["name"],
                    "type": c["data_type"],
                    "obligatoire": not c["nullable"],
                    "clé primaire": c["is_primary_key"],
                }
                for c in table["columns"]
            ],
            use_container_width=True,
        )
        if table.get("primary_key"):
            st.caption(f"Clé(s) : {', '.join(table['primary_key'])}")

    return table


def _run_execution(
    client: ApiClient,
    *,
    project_id: str,
    table: dict,
    count: int,
    context_query: str,
    mode: str,
    export_format: str,
    insert_target: dict | None,
    confirm_insert: bool,
) -> None:
    entity_payload = build_entity_spec_payload(table)
    payload = build_generation_payload(
        project_id=project_id,
        entity=entity_payload,
        count=count,
        context_query=context_query or None,
        mode=mode,
        export_format=export_format,
        insert_target=insert_target,
        confirm_insert=confirm_insert,
    )
    st.session_state[state.LAST_PAYLOAD] = payload

    started_at = time.perf_counter()
    try:
        result = client.execute_generation(payload)
    except SmartDataGeneratorApiError as exc:
        st.error(f"Échec de l'exécution : {exc.message}")
        return
    duration = time.perf_counter() - started_at

    st.session_state[state.LAST_RESULT] = result
    st.session_state[state.LAST_DURATION] = duration
    st.success("Exécution terminée. Consultez la page Result pour le détail.")
