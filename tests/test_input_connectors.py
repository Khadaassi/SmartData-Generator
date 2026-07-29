from pathlib import Path

import pytest

from connectors.input import DataReaderError, read_csv, read_json


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


# --- CSV ---


def test_read_csv_returns_normalized_records(tmp_path):
    path = _write(tmp_path, "clients.csv", "nom, email\n Alice , alice@example.com\nBob,\n")

    records = read_csv(path)

    assert records == [
        {"nom": "Alice", "email": "alice@example.com"},
        {"nom": "Bob", "email": None},
    ]


def test_read_csv_supports_custom_delimiter(tmp_path):
    path = _write(tmp_path, "clients.csv", "nom;email\nAlice;alice@example.com\n")

    records = read_csv(path, delimiter=";")

    assert records == [{"nom": "Alice", "email": "alice@example.com"}]


def test_read_csv_missing_file_raises_data_reader_error(tmp_path):
    with pytest.raises(DataReaderError) as exc_info:
        read_csv(tmp_path / "missing.csv")

    assert exc_info.value.code == "file_not_found"


def test_read_csv_empty_file_raises_data_reader_error(tmp_path):
    path = _write(tmp_path, "empty.csv", "")

    with pytest.raises(DataReaderError) as exc_info:
        read_csv(path)

    assert exc_info.value.code == "empty_file"


def test_read_csv_ragged_row_raises_data_reader_error(tmp_path):
    path = _write(tmp_path, "ragged.csv", "nom,email\nAlice,alice@example.com,extra\n")

    with pytest.raises(DataReaderError) as exc_info:
        read_csv(path)

    assert exc_info.value.code == "malformed_row"


def test_read_csv_rejects_directory(tmp_path):
    with pytest.raises(DataReaderError) as exc_info:
        read_csv(tmp_path)

    assert exc_info.value.code == "not_a_file"


# --- JSON ---


def test_read_json_accepts_a_list_of_objects(tmp_path):
    path = _write(tmp_path, "clients.json", '[{"nom": " Alice ", "age": 30}, {"nom": "Bob", "age": null}]')

    records = read_json(path)

    assert records == [{"nom": "Alice", "age": 30}, {"nom": "Bob", "age": None}]


def test_read_json_wraps_a_single_object_into_a_list(tmp_path):
    path = _write(tmp_path, "client.json", '{"nom": "Alice"}')

    records = read_json(path)

    assert records == [{"nom": "Alice"}]


def test_read_json_normalizes_nested_structures(tmp_path):
    path = _write(tmp_path, "clients.json", '[{"nom": "Alice", "adresse": {"ville": " Paris "}, "tags": [" vip "]}]')

    records = read_json(path)

    assert records == [{"nom": "Alice", "adresse": {"ville": "Paris"}, "tags": ["vip"]}]


def test_read_json_missing_file_raises_data_reader_error(tmp_path):
    with pytest.raises(DataReaderError) as exc_info:
        read_json(tmp_path / "missing.json")

    assert exc_info.value.code == "file_not_found"


def test_read_json_invalid_syntax_raises_data_reader_error(tmp_path):
    path = _write(tmp_path, "invalid.json", "{not valid json")

    with pytest.raises(DataReaderError) as exc_info:
        read_json(path)

    assert exc_info.value.code == "json_parse_error"


def test_read_json_rejects_non_object_elements(tmp_path):
    path = _write(tmp_path, "invalid.json", '[{"nom": "Alice"}, "pas un objet"]')

    with pytest.raises(DataReaderError) as exc_info:
        read_json(path)

    assert exc_info.value.code == "invalid_json_structure"


def test_read_json_rejects_scalar_top_level_value(tmp_path):
    path = _write(tmp_path, "invalid.json", "42")

    with pytest.raises(DataReaderError) as exc_info:
        read_json(path)

    assert exc_info.value.code == "invalid_json_structure"
