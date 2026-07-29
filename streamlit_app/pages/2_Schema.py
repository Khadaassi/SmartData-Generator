import streamlit as st

from streamlit_app.api_client import get_api_client
from streamlit_app.components.api_status import render_api_status
from streamlit_app.components.schema_analysis import render_schema_analysis_form
from streamlit_app.state import init_session_state

init_session_state()
client = get_api_client()
api_available = render_api_status(client)

st.title("Schéma PostgreSQL")

if not api_available:
    st.error("L'API SmartData Generator est indisponible : l'analyse de schéma est désactivée.")
else:
    render_schema_analysis_form(client)
