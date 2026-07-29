import streamlit as st

from streamlit_app import state
from streamlit_app.api_client import get_api_client
from streamlit_app.components.api_status import render_api_status
from streamlit_app.components.generation_form import render_generation_form
from streamlit_app.state import init_session_state

init_session_state()
client = get_api_client()
api_available = render_api_status(client)

st.title("Génération")

if not st.session_state.get(state.PROJECT_ID):
    st.warning("Sélectionnez d'abord un projet dans la page Project.")
elif not api_available:
    st.error("L'API SmartData Generator est indisponible : la génération est désactivée.")
else:
    render_generation_form(client)
