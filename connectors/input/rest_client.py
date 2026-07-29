from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from connectors.input.errors import DataReaderError
from connectors.input.json_utils import extract_records
from connectors.input.normalize import normalize_records

AuthType = Literal["none", "bearer", "api_key", "basic"]


class RestAuthConfig(BaseModel):
    """Authentification appliquée à la requête. Rien n'est supposé : le type et
    les identifiants doivent être fournis explicitement (cf. technical_architecture.md
    section 6.25)."""

    type: AuthType = "none"

    # type="bearer"
    token: str | None = None

    # type="api_key"
    api_key_header: str = "X-API-Key"
    api_key_value: str | None = None

    # type="basic"
    username: str | None = None
    password: str | None = None


class RestSourceConfig(BaseModel):
    """Configuration d'une source REST. Aucun endpoint, format de réponse ou schéma
    d'authentification n'est supposé par défaut : tout est fourni par configuration."""

    url: str
    method: Literal["GET", "POST"] = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, str] = Field(default_factory=dict)
    json_body: dict | None = None
    timeout: float = 10.0
    auth: RestAuthConfig = Field(default_factory=RestAuthConfig)
    data_path: str | None = None  # ex: "data.items", pour extraire les enregistrements d'une réponse enveloppée


def _build_auth_headers(auth: RestAuthConfig) -> dict[str, str]:
    if auth.type == "bearer":
        if not auth.token:
            raise DataReaderError(code="invalid_auth_config", message="auth.token est requis pour le type 'bearer'.")
        return {"Authorization": f"Bearer {auth.token}"}
    if auth.type == "api_key":
        if not auth.api_key_value:
            raise DataReaderError(
                code="invalid_auth_config", message="auth.api_key_value est requis pour le type 'api_key'."
            )
        return {auth.api_key_header: auth.api_key_value}
    return {}


def _build_basic_auth(auth: RestAuthConfig) -> tuple[str, str] | None:
    if auth.type != "basic":
        return None
    if not auth.username or not auth.password:
        raise DataReaderError(
            code="invalid_auth_config", message="auth.username et auth.password sont requis pour le type 'basic'."
        )
    return (auth.username, auth.password)


def _resolve_data_path(content: Any, path: str, source: str) -> Any:
    current = content
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            raise DataReaderError(
                code="data_path_not_found", message=f"Chemin '{path}' introuvable dans la réponse de {source}."
            )
        current = current[key]
    return current


def fetch_json(config: RestSourceConfig, *, client: httpx.Client | None = None) -> Any:
    """Exécute la requête HTTP configurée et retourne le corps de la réponse parsé en JSON."""
    headers = {**config.headers, **_build_auth_headers(config.auth)}
    basic_auth = _build_basic_auth(config.auth)

    owns_client = client is None
    http_client = client or httpx.Client(timeout=config.timeout)

    try:
        response = http_client.request(
            config.method,
            config.url,
            headers=headers,
            params=config.params,
            json=config.json_body,
            auth=basic_auth,
        )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise DataReaderError(code="timeout", message=f"Délai dépassé pour {config.url} : {exc}") from exc
    except httpx.HTTPStatusError as exc:
        raise DataReaderError(
            code="http_error", message=f"Erreur HTTP {exc.response.status_code} pour {config.url} : {exc}"
        ) from exc
    except httpx.RequestError as exc:
        raise DataReaderError(code="connection_error", message=f"Erreur de connexion à {config.url} : {exc}") from exc
    finally:
        if owns_client:
            http_client.close()

    try:
        return response.json()
    except ValueError as exc:
        raise DataReaderError(code="invalid_json_response", message=f"Réponse non-JSON depuis {config.url} : {exc}") from exc


def read_rest(config: RestSourceConfig, *, client: httpx.Client | None = None) -> list[dict]:
    """Récupère des données depuis une API REST configurée et les retourne normalisées.

    `config.data_path` permet d'extraire la liste d'enregistrements d'une réponse
    enveloppée (ex. `{"data": {"items": [...]}}`) sans que le connecteur ait à
    deviner la structure de la réponse.
    """
    content = fetch_json(config, client=client)

    if config.data_path:
        content = _resolve_data_path(content, config.data_path, config.url)

    records = extract_records(content, source=config.url)
    return normalize_records(records)
