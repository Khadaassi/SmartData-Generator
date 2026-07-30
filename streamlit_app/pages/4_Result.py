import streamlit as st

from streamlit_app import state
from streamlit_app.api_client import get_api_client
from streamlit_app.components.api_status import render_api_status
from streamlit_app.components.data_preview import render_data_preview
from streamlit_app.components.execution_summary import render_execution_summary
from streamlit_app.components.validation_report import render_validation_report
from streamlit_app.state import init_session_state

init_session_state()
client = get_api_client()
render_api_status(client)

st.title("Résultat")

result = st.session_state.get(state.LAST_RESULT)
if not result:
    st.info("Aucune exécution récente. Lancez une génération depuis la page Generation.")
else:
    duration = st.session_state.get(state.LAST_DURATION)
    render_execution_summary(result, duration_seconds=duration)
    render_data_preview(result)
    render_validation_report(result)
