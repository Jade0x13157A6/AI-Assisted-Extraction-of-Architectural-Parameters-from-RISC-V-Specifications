#!/usr/bin/env python3
"""Validate the structure of the submitted RISC-V parameter YAML file."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn

import yaml


REQUIRED_PARAMETER_FIELDS = {
    "name",
    "description",
    "category",
    "type",
    "value",
    "implementation_specific",
    "constraints",
    "evidence",
    "confidence",
}

ALLOWED_CATEGORIES = {"implementation_parameter", "architectural_constant"}
ALLOWED_TYPES = {
    "integer",
    "string",
    "enum",
    "bit_field",
    "implementation_defined_structure",
}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}


def fail(message: str) -> NoReturn:
    raise SystemExit(f"INVALID: {message}")


def require_string_list(value: object, field: str, location: str) -> None:
    if not isinstance(value, list) or not value:
        fail(f"{location}.{field} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        fail(f"{location}.{field} must contain only non-empty strings")


def validate(path: Path) -> tuple[int, int]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except yaml.YAMLError as exc:
        fail(f"YAML syntax error: {exc}")

    if not isinstance(data, dict):
        fail("top-level YAML value must be a mapping")
    if not isinstance(data.get("schema_version"), str):
        fail("schema_version must be a string")

    snippets = data.get("snippets")
    if not isinstance(snippets, list) or not snippets:
        fail("snippets must be a non-empty list")

    parameter_count = 0
    names: set[tuple[str, str]] = set()

    for snippet_index, snippet in enumerate(snippets):
        snippet_location = f"snippets[{snippet_index}]"
        if not isinstance(snippet, dict):
            fail(f"{snippet_location} must be a mapping")

        source = snippet.get("source")
        if not isinstance(source, dict):
            fail(f"{snippet_location}.source must be a mapping")
        for field in ("document", "section", "topic"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                fail(f"{snippet_location}.source.{field} must be a non-empty string")

        parameters = snippet.get("parameters")
        if not isinstance(parameters, list):
            fail(f"{snippet_location}.parameters must be a list")

        for parameter_index, parameter in enumerate(parameters):
            location = f"{snippet_location}.parameters[{parameter_index}]"
            if not isinstance(parameter, dict):
                fail(f"{location} must be a mapping")

            missing = REQUIRED_PARAMETER_FIELDS - parameter.keys()
            if missing:
                fail(f"{location} is missing fields: {sorted(missing)}")

            name = parameter["name"]
            if not isinstance(name, str) or not name.strip():
                fail(f"{location}.name must be a non-empty string")

            unique_key = (source["section"], name)
            if unique_key in names:
                fail(f"duplicate parameter name in section {source['section']}: {name}")
            names.add(unique_key)

            if parameter["category"] not in ALLOWED_CATEGORIES:
                fail(f"{location}.category is not allowed")
            if parameter["type"] not in ALLOWED_TYPES:
                fail(f"{location}.type is not allowed")
            if not isinstance(parameter["implementation_specific"], bool):
                fail(f"{location}.implementation_specific must be boolean")
            if parameter["confidence"] not in ALLOWED_CONFIDENCE:
                fail(f"{location}.confidence is not allowed")

            expected_flag = parameter["category"] == "implementation_parameter"
            if parameter["implementation_specific"] != expected_flag:
                fail(f"{location} has inconsistent category and implementation_specific")

            require_string_list(parameter["constraints"], "constraints", location)
            require_string_list(parameter["evidence"], "evidence", location)
            parameter_count += 1

        for list_field in ("non_parameter_requirements", "excluded_candidates"):
            if not isinstance(snippet.get(list_field), list):
                fail(f"{snippet_location}.{list_field} must be a list")

    return len(snippets), parameter_count


def main() -> None:
    yaml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/results.yaml")
    snippet_count, parameter_count = validate(yaml_path)
    print(f"VALID: {snippet_count} snippets and {parameter_count} parameters checked.")


if __name__ == "__main__":
    main()
