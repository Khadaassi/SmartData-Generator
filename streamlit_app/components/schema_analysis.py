import streamlit as st

from streamlit_app import state
from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError
from streamlit_app.security import mask_database_url


def render_schema_analysis_form(client: ApiClient) -> None:
    st.subheader("Analyse du schéma PostgreSQL")
    with st.form("schema_analysis_form"):
        database_url = st.text_input(
            "URL PostgreSQL",
            type="password",
            help="Ex : postgresql+psycopg://user:password@host:5432/dbname",
        )
        schema_name = st.text_input("Schéma PostgreSQL", value="public")
        submitted = st.form_submit_button("Analyser le schéma")

    if submitted:
        if not database_url:
            st.error("L'URL PostgreSQL est requise.")
        else:
            try:
                result = client.analyze_postgres_schema(
                    {"database_url": database_url, "schema_name": schema_name or "public"}
                )
            except SmartDataGeneratorApiError as exc:
                st.error(f"Analyse impossible : {exc.message}")
            else:
                st.session_state[state.SCHEMA_RESULT] = result
                st.session_state[state.SELECTED_ENTITY] = None
                st.success(f"Schéma `{result['schema_name']}` analysé : {len(result['tables'])} table(s).")
                st.caption(f"Connexion analysée : {mask_database_url(database_url)}")

    render_schema_result()


def render_schema_result() -> None:
    result = st.session_state.get(state.SCHEMA_RESULT)
    if not result:
        st.info("Aucun schéma analysé pour le moment.")
        return

    st.write("**Ordre de génération** : " + " → ".join(result.get("generation_order", [])))

    for table in result.get("tables", []):
        with st.expander(f"Table `{table['name']}` ({len(table['columns'])} colonne(s))"):
            st.dataframe(
                [
                    {
                        "colonne": c["name"],
                        "type": c["data_type"],
                        "nullable": c["nullable"],
                        "clé primaire": c["is_primary_key"],
                        "unique": c["is_unique"],
                        "défaut": c.get("default"),
                    }
                    for c in table["columns"]
                ],
                use_container_width=True,
            )
            if table.get("primary_key"):
                st.caption(f"Clé primaire : {', '.join(table['primary_key'])}")
            if table.get("foreign_keys"):
                st.write("**Clés étrangères**")
                st.dataframe(table["foreign_keys"], use_container_width=True)
            if table.get("unique_constraints"):
                st.write("**Contraintes uniques**")
                st.dataframe(table["unique_constraints"], use_container_width=True)
            if table.get("check_constraints"):
                st.write("**Contraintes CHECK**")
                st.dataframe(table["check_constraints"], use_container_width=True)
