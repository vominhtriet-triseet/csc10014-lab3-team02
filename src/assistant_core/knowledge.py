"""Load and search office-directory and handbook data."""

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from assistant_core.errors import DataError


@dataclass(frozen=True)
class Office:
    """A university office and its location/opening hours."""

    name: str
    room: str
    hours: str


class OfficeDirectory:
    """An in-memory directory loaded once from a UTF-8 CSV file."""

    _REQUIRED_COLUMNS = ("name", "room", "hours")

    def __init__(self, offices: list[Office]) -> None:
        self._offices = tuple(offices)

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        try:
            with path.open("r", encoding="utf-8", newline="") as csv_file:
                reader = csv.DictReader(csv_file, strict=True)
                fieldnames = reader.fieldnames
                if fieldnames is None:
                    raise DataError(f"CSV file has no header: {path}")
                missing = [column for column in cls._REQUIRED_COLUMNS if column not in fieldnames]
                if missing:
                    raise DataError(f"CSV file is missing required column(s) {missing}: {path}")

                offices: list[Office] = []
                for line_number, row in enumerate(reader, start=2):
                    # DictReader uses None for extra fields and for missing cells.
                    if None in row or any(row.get(col) is None for col in cls._REQUIRED_COLUMNS):
                        raise DataError(f"Malformed CSV row at line {line_number}: {path}")
                    values = {col: row[col].strip() for col in cls._REQUIRED_COLUMNS}
                    if any(not value for value in values.values()):
                        raise DataError(f"Empty required value at line {line_number}: {path}")
                    offices.append(Office(**values))
                return cls(offices)
        except OSError as exc:
            raise DataError(f"Cannot read CSV file {path}: {exc}") from exc
        except csv.Error as exc:
            raise DataError(f"Malformed CSV file {path}: {exc}") from exc

    @property
    def names(self) -> tuple[str, ...]:
        """Office names in file order."""
        return tuple(office.name for office in self._offices)

    def find(self, text: str) -> Office | None:
        """Find the first office whose name contains text, case-insensitively."""
        needle = text.strip().casefold()
        if not needle:
            return None
        return next(
            (office for office in self._offices if needle in office.name.casefold()),
            None,
        )


@dataclass(frozen=True)
class Rule:
    """A handbook rule."""

    id: str
    title: str
    text: str


class Handbook:
    """An in-memory collection of rules loaded once from a JSON file."""

    def __init__(self, rules: list[Rule]) -> None:
        self._rules = tuple(rules)

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        try:
            with path.open("r", encoding="utf-8") as json_file:
                payload: Any = json.load(json_file)
        except OSError as exc:
            raise DataError(f"Cannot read JSON file {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise DataError(f"Malformed JSON file {path}: {exc}") from exc

        # Accept a JSON array, or an object with a "rules" array.
        if isinstance(payload, dict):
            if "rules" not in payload:
                raise DataError(f"JSON object must contain a 'rules' array: {path}")
            payload = payload["rules"]
        if not isinstance(payload, list):
            raise DataError(f"JSON data must be a list of rules: {path}")

        rules: list[Rule] = []
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise DataError(f"Rule at index {index} must be an object: {path}")
            if not all(key in item for key in ("id", "title", "text")):
                raise DataError(f"Rule at index {index} must contain id, title, and text: {path}")
            if not all(isinstance(item[key], str) and item[key].strip() for key in ("id", "title", "text")):
                raise DataError(f"Rule at index {index} has an empty or non-string field: {path}")
            rules.append(
                Rule(
                    id=item["id"].strip(),
                    title=item["title"].strip(),
                    text=item["text"].strip(),
                )
            )
        return cls(rules)

    def search(self, query: str) -> Rule | None:
        """Return the rule with the greatest keyword overlap; ties keep file order."""
        terms = set(re.findall(r"\w+", query.casefold()))
        if not terms:
            return None

        best_rule: Rule | None = None
        best_score = 0
        for rule in self._rules:
            rule_terms = set(re.findall(r"\w+", f"{rule.title} {rule.text}".casefold()))
            score = len(terms & rule_terms)
            if score > best_score:
                best_rule = rule
                best_score = score
        return best_rule
