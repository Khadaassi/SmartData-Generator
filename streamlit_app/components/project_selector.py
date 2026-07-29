import streamlit as st

from streamlit_app import state
from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError


def render_project_selector(client: ApiClient) -> str | None:
    st.subheader("Projet")

    try:
        projects = client.list_projects()
    except SmartDataGeneratorApiError as exc:
        st.error(exc.message)
        projects = []

    current_id = st.session_state.get(state.PROJECT_ID)
    project_id = _render_picker(projects, current_id)
    _render_creation_form(client)

    st.session_state[state.PROJECT_ID] = project_id
    st.caption(f"Projet actif : `{project_id or '—'}`")
    return project_id


def _render_picker(projects: list[dict], current_id: str | None) -> str | None:
    if not projects:
        st.info("Aucun projet existant. Créez-en un ci-dessous.")
        return None

    options = [project["id"] for project in projects]
    labels = {project["id"]: f"{project['name']} ({project['id'][:8]})" for project in projects}
    index = options.index(current_id) if current_id in options else 0

    return st.selectbox(
        "Sélectionner un projet",
        options,
        index=index,
        format_func=lambda project_id: labels[project_id],
    )


def _render_creation_form(client: ApiClient) -> None:
    with st.expander("Créer un nouveau projet"):
        name = st.text_input("Nom du projet", key="new_project_name")
        description = st.text_area("Description (optionnel)", key="new_project_description")

        if st.button("Créer le projet", disabled=not name):
            try:
                project = client.create_project({"name": name, "description": description or None})
            except SmartDataGeneratorApiError as exc:
                st.error(exc.message)
                return

            st.session_state[state.PROJECT_ID] = project["id"]
            st.success(f"Projet « {project['name']} » créé.")
            st.rerun()
