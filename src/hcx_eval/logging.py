"""Logging helpers that enforce the shared redaction boundary."""

from collections.abc import Mapping

from pydantic import JsonValue

from hcx_eval.security import redact_mapping


def safe_log_fields(fields: Mapping[str, JsonValue]) -> dict[str, JsonValue]:
    """Build structured fields that are safe to pass to a logger."""
    return redact_mapping(fields)
