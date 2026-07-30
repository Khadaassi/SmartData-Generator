import streamlit as st

from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError
from streamlit_app.security import mask_database_url

CONFIRMATION_LABEL = "Je confirme l'import de ces données dans la table cible."

_AUTH_TYPES = ["none", "bearer", "api_key", "basic"]


def render_data_import_form(client: ApiClient) -> None:
    st.subheader("Import direct en base")
    st.caption(
        "Charge des données déjà correctes (fichier ou API REST) directement dans une table "
        "PostgreSQL existante, sans passer par la génération LLM."
    )

    source_label = st.radio("Source", ["CSV", "JSON", "REST"], horizontal=True, key="import_format")

    if source_label == "REST":
        _render_rest_import(client)
    else:
        _render_file_import(client, source_label)


def _render_file_import(client: ApiClient, source_label: str) -> None:
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

    if st.button("Lancer l'import", disabled=disabled, type="primary", key="import_file_button"):
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

        _render_success(result, database_url)


def _parse_key_value_lines(raw: str) -> dict[str, str]:
    """Parse des lignes 'Clé: Valeur' en dict ; ignore les lignes vides ou mal formées."""
    result: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key:
            result[key] = value.strip()
    return result


def _render_rest_auth_fields() -> dict:
    auth_type = st.selectbox("Authentification", _AUTH_TYPES, key="import_rest_auth_type")
    auth: dict = {"type": auth_type}

    if auth_type == "bearer":
        auth["token"] = st.text_input("Token", type="password", key="import_rest_auth_token")
    elif auth_type == "api_key":
        auth["api_key_header"] = st.text_input(
            "Nom de l'en-tête", value="X-API-Key", key="import_rest_auth_header"
        )
        auth["api_key_value"] = st.text_input("Valeur de la clé", type="password", key="import_rest_auth_key")
    elif auth_type == "basic":
        auth["username"] = st.text_input("Utilisateur", key="import_rest_auth_user")
        auth["password"] = st.text_input("Mot de passe", type="password", key="import_rest_auth_pass")

    return auth


def _render_rest_import(client: ApiClient) -> None:
    st.caption(
        "Interroge une API REST externe (URL, authentification et chemin d'extraction fournis "
        "explicitement, rien n'est supposé) et insère les enregistrements obtenus tels quels."
    )

    url = st.text_input("URL de l'API", key="import_rest_url", help="Ex : https://api.exemple.com/villes")
    method = st.selectbox("Méthode HTTP", ["GET", "POST"], key="import_rest_method")
    data_path = st.text_input(
        "Chemin d'extraction (optionnel)",
        key="import_rest_data_path",
        help="Ex : data.items, si la réponse enveloppe la liste d'enregistrements (ex. {\"data\": {\"items\": [...]}}).",
    )

    with st.expander("En-têtes / paramètres / authentification (optionnel)"):
        headers_raw = st.text_area(
            "En-têtes HTTP (une ligne par en-tête, format 'Clé: Valeur')", key="import_rest_headers"
        )
        params_raw = st.text_area(
            "Paramètres de requête (une ligne par paramètre, format 'Clé: Valeur')", key="import_rest_params"
        )
        auth = _render_rest_auth_fields()

    database_url = st.text_input(
        "URL PostgreSQL cible",
        type="password",
        help="Ex : postgresql+psycopg://user:password@host:5432/dbname",
        key="import_rest_db_url",
    )
    schema_name = st.text_input("Schéma cible", value="public", key="import_rest_schema")
    table = st.text_input("Table cible", key="import_rest_table")

    st.warning("Cette opération écrira des données dans la base cible.")
    confirm = st.checkbox(CONFIRMATION_LABEL, key="import_rest_confirm_checkbox")

    disabled = not url or not database_url or not table or not confirm

    if st.button("Lancer l'import", disabled=disabled, type="primary", key="import_rest_button"):
        source = {
            "url": url,
            "method": method,
            "headers": _parse_key_value_lines(headers_raw),
            "params": _parse_key_value_lines(params_raw),
            "auth": auth,
            "data_path": data_path or None,
        }
        try:
            result = client.import_rest_data(
                source=source, database_url=database_url, schema_name=schema_name, table=table, confirm=confirm
            )
        except SmartDataGeneratorApiError as exc:
            st.error(f"Import échoué : {exc.message}")
            return

        _render_success(result, database_url)


def _render_success(result: dict, database_url: str) -> None:
    st.success(
        f"Import réussi : {result['rows_inserted']}/{result['rows_read']} ligne(s) insérée(s) "
        f"dans `{result['schema_name']}.{result['table']}`."
    )
    st.caption(f"Connexion utilisée : {mask_database_url(database_url)}")
