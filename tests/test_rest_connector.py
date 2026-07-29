import httpx
import pytest

from connectors.input import (
    DataReaderError,
    RestAuthConfig,
    RestSourceConfig,
    read_rest,
)


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_read_rest_returns_normalized_records():
    def handler(request):
        return httpx.Response(200, json=[{"nom": " Alice "}, {"nom": "Bob"}])

    config = RestSourceConfig(url="https://api.example.com/clients")

    records = read_rest(config, client=_client(handler))

    assert records == [{"nom": "Alice"}, {"nom": "Bob"}]


def test_read_rest_wraps_a_single_object_into_a_list():
    def handler(request):
        return httpx.Response(200, json={"nom": "Alice"})

    config = RestSourceConfig(url="https://api.example.com/clients")

    records = read_rest(config, client=_client(handler))

    assert records == [{"nom": "Alice"}]


def test_read_rest_extracts_records_via_data_path():
    def handler(request):
        return httpx.Response(200, json={"data": {"items": [{"nom": "Alice"}]}})

    config = RestSourceConfig(url="https://api.example.com/clients", data_path="data.items")

    records = read_rest(config, client=_client(handler))

    assert records == [{"nom": "Alice"}]


def test_read_rest_sends_query_params_and_headers():
    captured = {}

    def handler(request):
        captured["params"] = dict(request.url.params)
        captured["custom_header"] = request.headers.get("x-project-id")
        return httpx.Response(200, json=[])

    config = RestSourceConfig(
        url="https://api.example.com/clients",
        params={"page": "1"},
        headers={"X-Project-Id": "proj-1"},
    )

    read_rest(config, client=_client(handler))

    assert captured["params"] == {"page": "1"}
    assert captured["custom_header"] == "proj-1"


def test_read_rest_sends_bearer_token():
    captured = {}

    def handler(request):
        captured["authorization"] = request.headers.get("authorization")
        return httpx.Response(200, json=[])

    config = RestSourceConfig(
        url="https://api.example.com/clients",
        auth=RestAuthConfig(type="bearer", token="secret-token"),
    )

    read_rest(config, client=_client(handler))

    assert captured["authorization"] == "Bearer secret-token"


def test_read_rest_sends_api_key_header():
    captured = {}

    def handler(request):
        captured["key"] = request.headers.get("x-api-key")
        return httpx.Response(200, json=[])

    config = RestSourceConfig(
        url="https://api.example.com/clients",
        auth=RestAuthConfig(type="api_key", api_key_header="X-API-Key", api_key_value="abc123"),
    )

    read_rest(config, client=_client(handler))

    assert captured["key"] == "abc123"


def test_read_rest_sends_basic_auth():
    captured = {}

    def handler(request):
        captured["authorization"] = request.headers.get("authorization")
        return httpx.Response(200, json=[])

    config = RestSourceConfig(
        url="https://api.example.com/clients",
        auth=RestAuthConfig(type="basic", username="user", password="pass"),
    )

    read_rest(config, client=_client(handler))

    assert captured["authorization"] is not None
    assert captured["authorization"].startswith("Basic ")


def test_read_rest_missing_bearer_token_raises_data_reader_error():
    config = RestSourceConfig(url="https://api.example.com/clients", auth=RestAuthConfig(type="bearer"))

    with pytest.raises(DataReaderError) as exc_info:
        read_rest(config)

    assert exc_info.value.code == "invalid_auth_config"


def test_read_rest_http_error_raises_data_reader_error():
    def handler(request):
        return httpx.Response(404, json={"error": "not found"})

    config = RestSourceConfig(url="https://api.example.com/missing")

    with pytest.raises(DataReaderError) as exc_info:
        read_rest(config, client=_client(handler))

    assert exc_info.value.code == "http_error"


def test_read_rest_connection_error_raises_data_reader_error():
    def handler(request):
        raise httpx.ConnectError("boom", request=request)

    config = RestSourceConfig(url="https://api.example.com/clients")

    with pytest.raises(DataReaderError) as exc_info:
        read_rest(config, client=_client(handler))

    assert exc_info.value.code == "connection_error"


def test_read_rest_timeout_raises_data_reader_error():
    def handler(request):
        raise httpx.TimeoutException("timed out", request=request)

    config = RestSourceConfig(url="https://api.example.com/clients")

    with pytest.raises(DataReaderError) as exc_info:
        read_rest(config, client=_client(handler))

    assert exc_info.value.code == "timeout"


def test_read_rest_invalid_json_response_raises_data_reader_error():
    def handler(request):
        return httpx.Response(200, content=b"not json")

    config = RestSourceConfig(url="https://api.example.com/clients")

    with pytest.raises(DataReaderError) as exc_info:
        read_rest(config, client=_client(handler))

    assert exc_info.value.code == "invalid_json_response"


def test_read_rest_missing_data_path_raises_data_reader_error():
    def handler(request):
        return httpx.Response(200, json={"other": []})

    config = RestSourceConfig(url="https://api.example.com/clients", data_path="data.items")

    with pytest.raises(DataReaderError) as exc_info:
        read_rest(config, client=_client(handler))

    assert exc_info.value.code == "data_path_not_found"


def test_read_rest_rejects_non_object_elements():
    def handler(request):
        return httpx.Response(200, json=[{"nom": "Alice"}, "pas un objet"])

    config = RestSourceConfig(url="https://api.example.com/clients")

    with pytest.raises(DataReaderError) as exc_info:
        read_rest(config, client=_client(handler))

    assert exc_info.value.code == "invalid_json_structure"
