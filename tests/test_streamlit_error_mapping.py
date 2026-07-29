import httpx

from streamlit_app.api_client import SmartDataGeneratorApiError, _map_error_response
from streamlit_app.security import mask_database_url


def _response(status_code: int, json_body: dict) -> httpx.Response:
    return httpx.Response(status_code, json=json_body, request=httpx.Request("POST", "http://testserver/x"))


def test_map_422_uses_loc_and_msg_without_leaking_submitted_value():
    body = {
        "detail": [
            {
                "type": "string_type",
                "loc": ["body", "generation", "count"],
                "msg": "Input should be a valid integer",
                "input": "postgresql+psycopg://user:s3cr3t@localhost/db",
            }
        ]
    }

    error = _map_error_response(_response(422, body))

    assert isinstance(error, SmartDataGeneratorApiError)
    assert error.code == "validation_error"
    assert error.status_code == 422
    assert "s3cr3t" not in error.message
    assert "generation.count" in error.message


def test_map_502_preserves_connector_message():
    error = _map_error_response(_response(502, {"code": "connection_error", "message": "connexion refusée"}))

    assert error.status_code == 502
    assert error.code == "connection_error"
    assert error.message == "connexion refusée"


def test_map_500_hides_internal_details():
    body = {"code": "internal_error", "message": "Traceback (most recent call last): ..."}

    error = _map_error_response(_response(500, body))

    assert error.status_code == 500
    assert error.code == "internal_error"
    assert "Traceback" not in error.message
    assert error.message == "Une erreur interne est survenue côté service."


def test_map_error_response_without_json_body_still_produces_readable_message():
    response = httpx.Response(500, content=b"not json", request=httpx.Request("GET", "http://testserver/x"))

    error = _map_error_response(response)

    assert error.status_code == 500
    assert error.message


def test_mask_database_url_hides_password():
    masked = mask_database_url("postgresql+psycopg://user:s3cr3t@localhost:5432/dbname")

    assert "s3cr3t" not in masked
    assert masked == "postgresql+psycopg://user:***@localhost:5432/dbname"


def test_mask_database_url_without_credentials_is_unchanged():
    url = "postgresql+psycopg://localhost:5432/dbname"

    assert mask_database_url(url) == url


def test_mask_database_url_handles_empty_string():
    assert mask_database_url("") == ""
