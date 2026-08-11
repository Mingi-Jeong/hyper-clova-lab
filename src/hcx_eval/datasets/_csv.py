"""Strict UTF-8 CSV loading shared by protected structured datasets."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import TYPE_CHECKING

from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Collection
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class DatasetFormatError(ValueError):
    """A protected structured input violates its declared contract."""

    path: Path
    reason: str

    @override
    def __str__(self) -> str:
        return f"invalid dataset {self.path}: {self.reason}"


def read_csv_rows(
    path: Path,
    *,
    required_columns: Collection[str],
) -> tuple[dict[str, str], ...]:
    """Read one UTF-8 CSV into detached rows without changing its bytes."""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            fieldnames = reader.fieldnames
            if fieldnames is None:
                raise DatasetFormatError(path=path, reason="missing header row")
            missing = sorted(set(required_columns).difference(fieldnames))
            if missing:
                raise DatasetFormatError(
                    path=path,
                    reason=f"missing required columns: {', '.join(missing)}",
                )
            rows: list[dict[str, str]] = []
            for row_number, raw in enumerate(reader, start=2):
                if None in raw or any(value is None for value in raw.values()):
                    raise DatasetFormatError(
                        path=path,
                        reason=f"malformed row {row_number}",
                    )
                rows.append(
                    {
                        key: value
                        for key, value in raw.items()
                        if key is not None and value is not None
                    }
                )
    except UnicodeDecodeError as error:
        raise DatasetFormatError(path=path, reason="not valid UTF-8") from error
    except OSError as error:
        raise DatasetFormatError(path=path, reason="cannot read file") from error
    return tuple(rows)


def require_value(row: dict[str, str], column: str, *, path: Path, line: int) -> str:
    """Return a trimmed required cell or raise with its source position."""
    value = row[column].strip()
    if not value:
        raise DatasetFormatError(
            path=path,
            reason=f"empty {column!r} at row {line}",
        )
    return value
