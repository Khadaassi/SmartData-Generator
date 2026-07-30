import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from streamlit_app.api_client import get_api_client
from streamlit_app.components.api_status import render_api_status
from streamlit_app.components.project_selector import render_project_selector
from streamlit_app.config import get_settings
from streamlit_app.state import init_session_state

settings = get_settings()
st.set_page_config(page_title=settings.application_title, page_icon="🧬", layout="wide")

init_session_state()
client = get_api_client()
api_available = render_api_status(client)

st.title(settings.application_title)
st.caption(f"Environnement : {settings.environment}")

st.markdown(
    """
SmartData Generator génère des jeux de données synthétiques métier à partir d'un schéma
PostgreSQL, de règles métier et d'une documentation indexée (RAG), puis les valide avant
de les prévisualiser, de les exporter ou de les insérer.

Cette interface est un **client de l'API FastAPI** de SmartData Generator : elle ne contient
aucune logique de génération et n'accède à aucun composant interne (Groq, Ollama, ChromaDB,
PostgreSQL) directement.

Utilisez le menu à gauche pour suivre le parcours :
1. **Project** — sélectionner le projet.
2. **Schema** — analyser le schéma PostgreSQL cible.
3. **Generation** — choisir une entité et lancer une génération (Preview par défaut).
4. **Result** — consulter le résultat, le rapport de validation et la traçabilité.
5. **Import** — charger un fichier CSV/JSON déjà correct directement dans une table existante,
   sans passer par le LLM (ex. données déjà collectées par ailleurs).
"""
)

render_project_selector(client)

if not api_available:
    st.error(
        "L'API SmartData Generator est indisponible. Démarrez le service avant de poursuivre : "
        "`uv run uvicorn api.app:app --host 0.0.0.0 --port 8000`."
    )
