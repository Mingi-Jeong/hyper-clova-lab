"""Strict parsing for in-kind transfer restriction reasons."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from hcx_eval.datasets._csv import DatasetFormatError, read_csv_rows, require_value

if TYPE_CHECKING:
    from pathlib import Path

_COLUMNS = frozenset({"code", "reason_name", "description"})
_CODE_PATTERN = re.compile(r"^[0-9]{2}$")


class TransferReason(BaseModel):
    """One reviewed code-to-restriction mapping."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(pattern=r"^[0-9]{2}$")
    reason_name: str = Field(min_length=1)
    description: str = Field(min_length=1)


def load_transfer_reasons(path: Path) -> tuple[TransferReason, ...]:
    """Load and validate the protected transfer-code mapping."""
    rows = read_csv_rows(path, required_columns=_COLUMNS)
    records: list[TransferReason] = []
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        code = require_value(row, "code", path=path, line=line)
        if _CODE_PATTERN.fullmatch(code) is None:
            raise DatasetFormatError(path=path, reason=f"invalid code {code}")
        if code in seen:
            raise DatasetFormatError(path=path, reason=f"duplicate code {code}")
        seen.add(code)
        records.append(
            TransferReason(
                code=code,
                reason_name=require_value(row, "reason_name", path=path, line=line),
                description=require_value(row, "description", path=path, line=line),
            )
        )
    return tuple(records)
