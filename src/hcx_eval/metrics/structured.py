"""Deterministic JSON Schema and tool-argument metrics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from jsonschema import Draft202012Validator

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pydantic import JsonValue


@dataclass(frozen=True, slots=True)
class ToolArgumentScore:
    """Exact and flattened leaf-level tool argument agreement."""

    exact: bool
    precision: float
    recall: float
    f1: float


def json_schema_valid(instance: JsonValue, schema: Mapping[str, object]) -> bool:
    """Validate an instance against a checked Draft 2020-12 schema."""
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema).is_valid(  # pyright: ignore[reportUnknownMemberType]
        instance
    )


def _flatten(value: JsonValue, path: str = "$") -> set[str]:
    match value:
        case dict() as mapping:
            return {
                leaf
                for key, item in mapping.items()
                for leaf in _flatten(item, f"{path}.{key}")
            }
        case list() as items:
            return {
                leaf
                for index, item in enumerate(items)
                for leaf in _flatten(item, f"{path}[{index}]")
            }
        case scalar:
            encoded = json.dumps(scalar, ensure_ascii=False, sort_keys=True)
            return {f"{path}={encoded}"}


def tool_argument_score(
    actual: JsonValue,
    expected: JsonValue,
) -> ToolArgumentScore:
    """Score exact JSON equality and path/value leaf overlap."""
    actual_leaves = _flatten(actual)
    expected_leaves = _flatten(expected)
    correct = len(actual_leaves.intersection(expected_leaves))
    precision = (
        float(not expected_leaves)
        if not actual_leaves
        else correct / len(actual_leaves)
    )
    recall = (
        float(not actual_leaves)
        if not expected_leaves
        else correct / len(expected_leaves)
    )
    f1 = (
        0.0
        if precision + recall == 0
        else (2 * precision * recall) / (precision + recall)
    )
    return ToolArgumentScore(
        exact=actual == expected,
        precision=precision,
        recall=recall,
        f1=f1,
    )
