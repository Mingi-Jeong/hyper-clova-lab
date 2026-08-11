from __future__ import annotations

from typing import TYPE_CHECKING

from hcx_eval.security import REDACTED, redact

if TYPE_CHECKING:
    from pydantic import JsonValue


def test_redaction_masks_nested_secrets_and_case_insensitive_headers() -> None:
    # Given: secrets nested in mappings and lists with mixed-case header names.
    value: JsonValue = {
        "outer": [{"Api_Key": "one"}, {"aUtHoRiZaTiOn": "Bearer two"}],
        "safe": "visible",
    }

    # When: the value crosses a diagnostic or artifact boundary.
    result = redact(value)

    # Then: every sensitive value is replaced recursively.
    assert result == {
        "outer": [{"Api_Key": REDACTED}, {"aUtHoRiZaTiOn": REDACTED}],
        "safe": "visible",
    }


def test_redaction_masks_bearer_token_even_under_unknown_key() -> None:
    # Given: an authorization value under a nonstandard field.
    value: JsonValue = {"metadata": "Bearer abc.def.ghi"}

    # When: recursive redaction is applied.
    result = redact(value)

    # Then: token-shaped content cannot leak.
    assert result == {"metadata": REDACTED}
