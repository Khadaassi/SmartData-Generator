import streamlit as st

CONFIRMATION_LABEL = "Je confirme l'insertion des données validées."


def render_insert_confirmation(default_table: str) -> tuple[dict | None, bool]:
    """Affiche les champs requis pour une insertion PostgreSQL et retourne
    (insert_target, confirm_insert). L'insertion n'est jamais implicite : elle
    exige une cible explicite ET une case de confirmation cochée.
    """
    st.warning("Cette opération écrira des données dans la base cible.")
    database_url = st.text_input("URL PostgreSQL cible", type="password", key="insert_db_url")
    schema_name = st.text_input("Schéma cible", value="public", key="insert_schema")
    table = st.text_input("Table cible", value=default_table, key="insert_table")
    confirm_insert = st.checkbox(CONFIRMATION_LABEL, key="insert_confirm_checkbox")

    insert_target = None
    if database_url and schema_name and table:
        insert_target = {"database_url": database_url, "table": table, "schema_name": schema_name}

    return insert_target, confirm_insert
