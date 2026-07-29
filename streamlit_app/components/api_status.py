import streamlit as st

from streamlit_app import state
from streamlit_app.api_client import ApiClient, SmartDataGeneratorApiError


def render_api_status(client: ApiClient) -> bool:
    """Affiche la disponibilité de l'API dans la sidebar et la retourne.

    Toute erreur est interceptée : l'indisponibilité de l'API ne doit jamais
    provoquer une erreur Streamlit non contrôlée, seulement désactiver les
    actions dépendantes de l'API sur la page appelante.
    """
    with st.sidebar:
        st.subheader("SmartData Generator API")
        try:
            health = client.check_health()
        except SmartDataGeneratorApiError as exc:
            st.markdown("🔴 **Indisponible**")
            st.caption(exc.message)
            st.session_state[state.API_AVAILABLE] = False
            return False

        st.markdown(f"🟢 **Disponible** — v{health.get('version', '?')} ({health.get('environment', '?')})")
        st.session_state[state.API_AVAILABLE] = True
        return True
