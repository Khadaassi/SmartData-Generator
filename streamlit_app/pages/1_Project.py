import streamlit as st

from streamlit_app.api_client import get_api_client
from streamlit_app.components.api_status import render_api_status
from streamlit_app.components.project_selector import render_project_selector
from streamlit_app.state import init_session_state

init_session_state()
client = get_api_client()
render_api_status(client)

st.title("Projet")
render_project_selector()

st.markdown(
    "Rappel : la documentation métier et les règles du projet sélectionné doivent avoir été "
    "indexées au préalable dans SmartData Generator (corpus RAG et règles codées) pour que la "
    "génération produise des résultats pertinents. Cette indexation ne fait pas partie de cette "
    "interface."
)
