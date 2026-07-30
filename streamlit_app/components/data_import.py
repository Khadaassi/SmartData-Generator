import streamlit as st

from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError
from streamlit_app.security import mask_database_url

CONFIRMATION_LABEL = "Je confirme l'import de ces données dans la table cible."


def render_data_import_form(client: ApiClient) -> None:
    st.subheader("Import direct en base")
    st.caption(
        "Charge un fichier CSV ou JSON déjà correct (ex. catalogue produits scrapé) directement "
        "dans une table PostgreSQL existante, sans passer par la génération LLM."
    )

    source_label = st.radio("Format du fichier", ["CSV", "JSON"], horizontal=True, key="import_format")
    source_format = "csv" if source_label == "CSV" else "json"
    uploaded_file = st.file_uploader(
        "Fichier à importer", type=[source_format], key="import_file"
    )

    database_url = st.text_input(
        "URL PostgreSQL cible",
        type="password",
        help="Ex : postgresql+psycopg://user:password@host:5432/dbname",
        key="import_db_url",
    )
    schema_name = st.text_input("Schéma cible", value="public", key="import_schema")
    table = st.text_input("Table cible", key="import_table")
    delimiter = st.text_input("Délimiteur", value=",", key="import_delimiter") if source_format == "csv" else ","

    st.warning("Cette opération écrira des données dans la base cible.")
    confirm = st.checkbox(CONFIRMATION_LABEL, key="import_confirm_checkbox")

    disabled = uploaded_file is None or not database_url or not table or not confirm

    if st.button("Lancer l'import", disabled=disabled, type="primary"):
        try:
            result = client.import_data(
                source_format=source_format,
                filename=uploaded_file.name,
                content=uploaded_file.getvalue(),
                database_url=database_url,
                schema_name=schema_name,
                table=table,
                confirm=confirm,
                delimiter=delimiter,
            )
        except SmartDataGeneratorApiError as exc:
            st.error(f"Import échoué : {exc.message}")
            return

        st.success(
            f"Import réussi : {result['rows_inserted']}/{result['rows_read']} ligne(s) insérée(s) "
            f"dans `{result['schema_name']}.{result['table']}`."
        )
        st.caption(f"Connexion utilisée : {mask_database_url(database_url)}")
