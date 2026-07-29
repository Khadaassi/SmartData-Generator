import pytest

from connectors.input import read_csv, read_json
from connectors.output import DataWriterError, write_csv, write_json


def test_write_csv_round_trips_with_read_csv(tmp_path):
    items = [{"nom": "Alice", "age": 30}, {"nom": "Bob", "age": 25}]
    path = tmp_path / "out.csv"

    write_csv(items, path)

    assert read_csv(path) == [{"nom": "Alice", "age": "30"}, {"nom": "Bob", "age": "25"}]


def test_write_csv_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "dir" / "out.csv"

    write_csv([{"nom": "Alice"}], path)

    assert path.exists()


def test_write_csv_unions_keys_across_all_items(tmp_path):
    items = [{"nom": "Alice"}, {"nom": "Bob", "age": 25}]
    path = tmp_path / "out.csv"

    write_csv(items, path)

    assert path.read_text(encoding="utf-8").splitlines()[0] == "nom,age"


def test_write_csv_empty_items_raises_data_writer_error(tmp_path):
    with pytest.raises(DataWriterError) as exc_info:
        write_csv([], tmp_path / "out.csv")

    assert exc_info.value.code == "no_data"


def test_write_json_round_trips_with_read_json(tmp_path):
    items = [{"nom": "Alice"}, {"nom": "Bob"}]
    path = tmp_path / "out.json"

    write_json(items, path)

    assert read_json(path) == items


def test_write_json_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "dir" / "out.json"

    write_json([{"nom": "Alice"}], path)

    assert path.exists()


def test_write_json_empty_items_raises_data_writer_error(tmp_path):
    with pytest.raises(DataWriterError) as exc_info:
        write_json([], tmp_path / "out.json")

    assert exc_info.value.code == "no_data"
