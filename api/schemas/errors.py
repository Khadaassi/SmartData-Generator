from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Corps de réponse uniforme pour toute erreur renvoyée par l'API."""

    code: str
    message: str
