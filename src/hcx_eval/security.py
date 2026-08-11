"""Secret-safe serialization boundaries."""

from __future__ import annotations

import re
import shlex
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, TypeAlias

from typing_extensions import override

if TYPE_CHECKING:
    from pydantic import JsonValue

REDACTED: Final = "[REDACTED]"
_SENSITIVE_KEY_LEAVES: Final = frozenset(
    {
        "api_key",
        "auth",
        "authorization",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "password",
        "secret",
        "token",
    }
)
_BEARER_PATTERN: Final = re.compile(r"\bbearer\s+\S+", re.IGNORECASE)
_CLI_EQUALS_PATTERN: Final = re.compile(
    r"(?P<option>--(?:api-key|authorization))=(?P<secret>\S+)", re.IGNORECASE
)
_ASSIGNMENT_KEY: Final = r"(?<![\w-])(?P<key>[A-Za-z][A-Za-z0-9_-]*)"
_ASSIGNMENT_PREFIX: Final = rf"{_ASSIGNMENT_KEY}(?P<separator>\s*=\s*)"
_QUOTED_ASSIGNMENT_VALUE: Final = r"(?P<quote>['\"])(.*?)(?P=quote)"
_BARE_ASSIGNMENT_VALUE: Final = (
    rf"(?!['\"])(?!{re.escape(REDACTED)})"
    r"[^\s,;&)\]}]+?(?=(?:[,;&)\]}]|\.(?:\s|$)|\s|$))"
)
_ASSIGNMENT_PATTERN: Final = re.compile(
    rf"{_ASSIGNMENT_PREFIX}(?:{_QUOTED_ASSIGNMENT_VALUE}|{_BARE_ASSIGNMENT_VALUE})",
    re.IGNORECASE,
)
JsonScalar: TypeAlias = str | int | float | bool | None


def _sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", key.casefold()).strip("_")
    if normalized == "apikey":
        normalized = "api_key"
    return any(
        normalized == leaf or normalized.endswith(f"_{leaf}")
        for leaf in _SENSITIVE_KEY_LEAVES
    )


def _redact_assignment(match: re.Match[str]) -> str:
    key = match.group("key")
    if not _sensitive_key(key):
        return match.group(0)
    quote = match.group("quote") or ""
    return f"{key}{match.group('separator')}{quote}{REDACTED}{quote}"


def redact_text(value: str) -> str:
    """Mask credential substrings while preserving surrounding useful text."""
    value = _ASSIGNMENT_PATTERN.sub(_redact_assignment, value)
    value = _CLI_EQUALS_PATTERN.sub(
        lambda match: f"{match.group('option')}={REDACTED}", value
    )
    return _BEARER_PATTERN.sub(f"Bearer {REDACTED}", value)


def redact_cli_invocation(invocation: str) -> str:
    """Mask split and equals-style CLI credentials while retaining arguments."""
    parts = shlex.split(redact_text(invocation))
    redacted: list[str] = []
    mask_next = False
    for part in parts:
        if mask_next:
            redacted.append(REDACTED)
            mask_next = False
        elif part.casefold() in {"--api-key", "--authorization"}:
            redacted.append(part)
            mask_next = True
        else:
            redacted.append(redact_text(part))
    return " ".join(redacted)


def redact(value: JsonValue) -> JsonValue:
    """Return a recursively redacted JSON-compatible copy."""
    match value:
        case dict() as mapping:
            return {
                key: REDACTED if _sensitive_key(key) else redact(item)
                for key, item in mapping.items()
            }
        case list() as items:
            return [redact(item) for item in items]
        case str() as text:
            return redact_text(text)
        case scalar:
            return scalar


def redact_mapping(value: Mapping[str, JsonValue]) -> dict[str, JsonValue]:
    """Redact a mapping while preserving a concrete JSON object return type."""
    return {
        key: REDACTED if _sensitive_key(key) else redact(item)
        for key, item in value.items()
    }


@dataclass(frozen=True, slots=True)
class FrozenJson:
    """Recursively immutable JSON value with explicit thawing for serialization."""

    value: JsonScalar | tuple[FrozenJson, ...] | FrozenDict

    def to_json(self) -> JsonValue:
        """Return a detached JSON-compatible representation."""
        match self.value:
            case FrozenDict() as mapping:
                return mapping.to_json()
            case tuple() as items:
                return [item.to_json() for item in items]
            case scalar:
                return scalar


@dataclass(frozen=True, slots=True)
class FrozenDict(Mapping[str, FrozenJson]):
    """Tuple-backed immutable mapping for validated JSON objects."""

    entries: tuple[tuple[str, FrozenJson], ...] = ()

    @override
    def __getitem__(self, key: str) -> FrozenJson:
        """Return an immutable value for key."""
        for candidate, value in self.entries:
            if candidate == key:
                return value
        raise KeyError(key)

    @override
    def __iter__(self) -> Iterator[str]:
        """Iterate keys in source order."""
        return (key for key, _ in self.entries)

    @override
    def __len__(self) -> int:
        """Return the number of keys."""
        return len(self.entries)

    def to_json(self) -> dict[str, JsonValue]:
        """Return a detached JSON-compatible dictionary."""
        return {key: value.to_json() for key, value in self.entries}


def freeze_json(value: JsonValue) -> FrozenJson:
    """Deep-copy JSON into recursively immutable containers."""
    match value:
        case dict() as mapping:
            return FrozenJson(freeze_mapping(mapping))
        case list() as items:
            return FrozenJson(tuple(freeze_json(item) for item in items))
        case scalar:
            return FrozenJson(scalar)


def freeze_mapping(value: Mapping[str, JsonValue]) -> FrozenDict:
    """Deep-copy a JSON mapping into a recursively immutable mapping."""
    return FrozenDict(tuple((key, freeze_json(item)) for key, item in value.items()))
