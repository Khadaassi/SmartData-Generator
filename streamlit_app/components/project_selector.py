import streamlit as st

from streamlit_app import state


def render_project_selector() -> str:
    st.subheader("Projet")
    project_id = st.text_input(
        "Project ID",
        value=st.session_state.get(state.PROJECT_ID, state.DEMO_PROJECT_ID),
        help="Identifiant du projet SmartData Generator à utiliser pour cette session.",
    )
    st.session_state[state.PROJECT_ID] = project_id

    if project_id == state.DEMO_PROJECT_ID:
        st.info(
            "Projet de démonstration : **Pricing Control Tower**. La documentation métier et "
            "les règles de ce projet doivent avoir été indexées au préalable dans SmartData "
            "Generator pour que la génération produise des résultats pertinents."
        )

    st.caption(f"Projet actif : `{project_id or '—'}`")
    return project_id
