import json
from dataclasses import FrozenInstanceError

import pytest

from assistant_core.errors import DataError
from assistant_core.knowledge import Handbook, Office, OfficeDirectory, Rule


def test_office_directory_loads_and_finds_case_insensitively(tmp_path):
    path = tmp_path / "offices.csv"
    path.write_text(
        "name,room,hours\nStudent Affairs,A101,08:00-17:00\nLibrary,B202,07:00-21:00\n",
        encoding="utf-8",
    )

    directory = OfficeDirectory.from_csv(path)

    assert directory.names == ("Student Affairs", "Library")
    assert directory.find("STUDENT") == Office("Student Affairs", "A101", "08:00-17:00")
    assert directory.find("missing") is None
    with pytest.raises(FrozenInstanceError):
        directory.find("library").name = "Changed"


def test_office_directory_missing_file_raises_data_error(tmp_path):
    with pytest.raises(DataError):
        OfficeDirectory.from_csv(tmp_path / "missing.csv")


@pytest.mark.parametrize(
    "contents",
    [
        "name,room\nLibrary,B202\n",
        "name,room,hours\nLibrary,B202\n",
        "name,room,hours\nLibrary,B202,07:00,extra\n",
        "name,room,hours\n, B202,07:00\n",
    ],
)
def test_office_directory_malformed_csv_raises_data_error(tmp_path, contents):
    path = tmp_path / "bad.csv"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(DataError):
        OfficeDirectory.from_csv(path)


def test_handbook_loads_and_searches_deterministically(tmp_path):
    path = tmp_path / "handbook.json"
    path.write_text(
        json.dumps({"rules": [
            {"id": "R1", "title": "Exam registration", "text": "Register before deadline"},
            {"id": "R2", "title": "Tuition payment", "text": "Pay fees before deadline"},
        ]}),
        encoding="utf-8",
    )

    handbook = Handbook.from_json(path)

    assert handbook.search("EXAM registration") == Rule(
        "R1", "Exam registration", "Register before deadline"
    )
    assert handbook.search("unrelated words") is None
    # Both rules overlap on "deadline"; equal scores preserve file order.
    assert handbook.search("deadline") == Rule(
        "R1", "Exam registration", "Register before deadline"
    )
    assert handbook.search("   ") is None


def test_handbook_accepts_json_array(tmp_path):
    path = tmp_path / "handbook.json"
    path.write_text(
        json.dumps([{"id": "A", "title": "Title", "text": "Body"}]),
        encoding="utf-8",
    )
    assert Handbook.from_json(path).search("body").id == "A"


def test_handbook_missing_file_raises_data_error(tmp_path):
    with pytest.raises(DataError):
        Handbook.from_json(tmp_path / "missing.json")


@pytest.mark.parametrize(
    "contents",
    [
        "{not valid json",
        '{"rules": [{"id": "R1", "title": "Only title"}]}',
        '{"rules": "not a list"}',
        '{"rules": [{"id": "", "title": "Title", "text": "Body"}]}',
        '{"rules": [42]}',
    ],
)
def test_handbook_malformed_json_raises_data_error(tmp_path, contents):
    path = tmp_path / "bad.json"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(DataError):
        Handbook.from_json(path)
