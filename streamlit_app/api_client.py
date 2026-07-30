from typing import Any

import httpx
import streamlit as st

from streamlit_app.config import StreamlitSettings, get_settings


class SmartDataGeneratorApiError(RuntimeError):
    """Erreur lisible représentant un échec d'appel à l'API SmartData Generator.

    Ne porte jamais de stack trace ni de valeur brute soumise par l'utilisateur
    (cf. gestion des erreurs 422 ci-dessous) : seul un message et un code stables
    sont exposés à l'interface.
    """

    def __init__(self, code: str, message: str, status_code: int | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ApiClient:
    def __init__(self, settings: StreamlitSettings | None = None, *, client: httpx.Client | None = None):
        self._settings = settings or get_settings()
        self._client = client or httpx.Client(
            base_url=self._settings.api_base_url, timeout=self._settings.request_timeout
        )

    def close(self) -> None:
        self._client.close()

    def check_health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def analyze_postgres_schema(self, payload: dict) -> dict[str, Any]:
        return self._request("POST", "/schema/postgres", json=payload)

    def execute_generation(self, payload: dict) -> dict[str, Any]:
        return self._request("POST", "/executions", json=payload)

    def create_project(self, payload: dict) -> dict[str, Any]:
        return self._request("POST", "/projects", json=payload)

    def list_projects(self) -> list[dict[str, Any]]:
        return self._request("GET", "/projects")

    def get_project(self, project_id: str) -> dict[str, Any]:
        return self._request("GET", f"/projects/{project_id}")

    def update_project_rules(self, project_id: str, rules: list[dict]) -> dict[str, Any]:
        return self._request("PUT", f"/projects/{project_id}/rules", json={"rules": rules})

    def upload_documents(self, project_id: str, files: list[tuple[str, bytes]]) -> dict[str, Any]:
        multipart_files = [("files", (name, content, "text/markdown")) for name, content in files]
        return self._request("POST", f"/projects/{project_id}/documents", files=multipart_files)

    def list_documents(self, project_id: str) -> dict[str, Any]:
        return self._request("GET", f"/projects/{project_id}/documents")

    def delete_document(self, project_id: str, filename: str) -> None:
        self._request("DELETE", f"/projects/{project_id}/documents/{filename}")

    def import_data(
        self,
        *,
        source_format: str,
        filename: str,
        content: bytes,
        database_url: str,
        schema_name: str,
        table: str,
        confirm: bool,
        delimiter: str = ",",
    ) -> dict[str, Any]:
        content_type = "text/csv" if source_format == "csv" else "application/json"
        data = {
            "database_url": database_url,
            "schema_name": schema_name,
            "table": table,
            "confirm": "true" if confirm else "false",
        }
        if source_format == "csv":
            data["delimiter"] = delimiter
        return self._request(
            "POST",
            f"/data-import/{source_format}",
            files={"file": (filename, content, content_type)},
            data=data,
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.TimeoutException as exc:
            raise SmartDataGeneratorApiError(
                code="timeout",
                message="Le service SmartData Generator n'a pas répondu à temps. Vérifiez qu'il est démarré.",
            ) from exc
        except httpx.ConnectError as exc:
            raise SmartDataGeneratorApiError(
                code="connection_error",
                message="Impossible de contacter l'API SmartData Generator. Vérifiez qu'elle est démarrée.",
            ) from exc
        except httpx.HTTPError as exc:
            raise SmartDataGeneratorApiError(
                code="network_error", message="Erreur réseau lors de l'appel à l'API SmartData Generator."
            ) from exc
        except Exception as exc:  # dernier filet : jamais d'erreur Streamlit non contrôlée
            raise SmartDataGeneratorApiError(
                code="unexpected_error", message="Erreur inattendue lors de l'appel à l'API."
            ) from exc

        if response.status_code >= 400:
            raise _map_error_response(response)

        return response.json() if response.content else {}


def _map_error_response(response: httpx.Response) -> SmartDataGeneratorApiError:
    status_code = response.status_code
    try:
        body = response.json()
    except ValueError:
        body = {}

    if status_code == 422:
        return SmartDataGeneratorApiError(
            code="validation_error", message=_format_validation_detail(body.get("detail")), status_code=status_code
        )

    code = body.get("code") or "http_error"
    message = body.get("message")

    if status_code == 502:
        message = message or "Le service externe (base de données) est inaccessible."
    elif status_code >= 500:
        code, message = "internal_error", "Une erreur interne est survenue côté service."
    elif not message:
        message = f"Erreur inattendue de l'API (code HTTP {status_code})."

    return SmartDataGeneratorApiError(code=code, message=message, status_code=status_code)


def _format_validation_detail(detail: Any) -> str:
    """Formate les erreurs 422 de FastAPI sans jamais recopier la valeur soumise
    (`input`) : un champ `database_url` invalide ne doit pas faire fuiter le
    mot de passe qu'il contenait dans le message affiché à l'utilisateur."""
    if isinstance(detail, str):
        return detail
    if not isinstance(detail, list) or not detail:
        return "La requête envoyée est invalide."

    lines = []
    for item in detail:
        loc = ".".join(str(part) for part in item.get("loc", []) if part != "body")
        msg = item.get("msg", "Champ invalide.")
        lines.append(f"{loc} : {msg}" if loc else msg)
    return "\n".join(lines)


@st.cache_resource
def get_api_client() -> ApiClient:
    return ApiClient()
