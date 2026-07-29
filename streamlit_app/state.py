import streamlit as st

API_AVAILABLE = "sdg_api_available"
PROJECT_ID = "sdg_project_id"
SCHEMA_RESULT = "sdg_schema_result"
SELECTED_ENTITY = "sdg_selected_entity"
LAST_PAYLOAD = "sdg_last_payload"
LAST_RESULT = "sdg_last_result"
LAST_DURATION = "sdg_last_duration"

DEMO_PROJECT_ID = "pricing-control-tower-demo"

_DEFAULTS = {
    API_AVAILABLE: None,
    PROJECT_ID: DEMO_PROJECT_ID,
    SCHEMA_RESULT: None,
    SELECTED_ENTITY: None,
    LAST_PAYLOAD: None,
    LAST_RESULT: None,
    LAST_DURATION: None,
}


def init_session_state() -> None:
    """Initialise l'état de session une seule fois par session Streamlit.

    Conserver ces valeurs entre les reruns évite qu'un simple rechargement de
    composant ne déclenche une nouvelle génération ou insertion involontaire.
    """
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value
