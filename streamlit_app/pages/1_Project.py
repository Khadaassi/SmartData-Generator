import streamlit as st

from streamlit_app.api_client import get_api_client
from streamlit_app.components.api_status import render_api_status
from streamlit_app.components.document_manager import render_document_manager
from streamlit_app.components.project_selector import render_project_selector
from streamlit_app.components.rule_builder import render_rule_builder
from streamlit_app.state import init_session_state

init_session_state()
client = get_api_client()
render_api_status(client)

st.title("Projet")
project_id = render_project_selector(client)

if project_id:
    render_document_manager(client, project_id)
    render_rule_builder(client, project_id)
else:
    st.info("Créez ou sélectionnez un projet pour gérer sa documentation métier et ses règles.")
