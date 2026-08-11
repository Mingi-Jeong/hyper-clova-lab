"""Secret-safe serialization boundaries."""

import re
from collections.abc import Mapping, Sequence
from typing import Final

from pydantic import JsonValue

REDACTED: Final = "[REDACTED]"
_SENSITIVE_FRAGMENTS: Final = (
    "apikey",
    "authorization",
    "cookie",
    "credential",
    "password",
    "secret",
    "token",
)
_BEARER_PATTERN: Final = re.compile(r"^\s*bearer\s+\S+", re.IGNORECASE)


def _sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.casefold())
    return any(fragment in normalized for fragment in _SENSITIVE_FRAGMENTS)


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
        case str() as text if _BEARER_PATTERN.match(text):
            return REDACTED
        case scalar:
            return scalar


def redact_mapping(value: Mapping[str, JsonValue]) -> dict[str, JsonValue]:
    """Redact a mapping while preserving a concrete JSON object return type."""
    return {
        key: REDACTED if _sensitive_key(key) else redact(item)
        for key, item in value.items()
    }


def redact_sequence(value: Sequence[JsonValue]) -> list[JsonValue]:
    """Redact a sequence for structured logging or artifacts."""
    return [redact(item) for item in value]
