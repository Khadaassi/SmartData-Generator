import pytest

from infrastructure.config import get_settings
from infrastructure.llm import get_llm

settings = get_settings()

pytestmark = pytest.mark.skipif(
    not settings.llm_api_key,
    reason="LLM_API_KEY (clé Groq) absente de l'environnement/.env",
)


def test_groq_chat_completion_responds():
    llm = get_llm()

    response = llm.invoke("Réponds uniquement par le mot: PONG")

    assert response.content.strip()
