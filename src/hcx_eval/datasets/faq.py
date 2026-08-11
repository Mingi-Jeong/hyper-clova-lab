"""Strict parsing for the reviewed default-option FAQ dataset."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from hcx_eval.datasets._csv import (
    DatasetFormatError,
    read_csv_rows,
    require_value,
)

if TYPE_CHECKING:
    from pathlib import Path

_FAQ_COLUMNS = frozenset(
    {
        "ID",
        "카테고리",
        "대표질문",
        "유사질문표현",
        "표준답변",
        "AI분기포인트",
        "근거구분",
        "근거ID",
    }
)
_SOURCE_COLUMNS = frozenset({"SourceID", "설명", "URL", "비고"})
_PARAPHRASE_SEPARATOR = re.compile(r"\s+/\s+")


class FaqSource(BaseModel):
    """One citation identifier from the protected source registry."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    source_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    url: str = Field(min_length=1)
    note: str


class FaqRecord(BaseModel):
    """Normalized FAQ row with reviewed answer and unreviewed paraphrases."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    faq_id: int = Field(gt=0)
    category: str = Field(min_length=1)
    representative_question: str = Field(min_length=1)
    paraphrases: tuple[str, ...] = Field(min_length=1)
    gold_answer: str = Field(min_length=1)
    required_facts: tuple[str, ...] = Field(min_length=1)
    source_kind: str = Field(min_length=1)
    source_ids: tuple[str, ...] = Field(min_length=1)


def _load_sources(path: Path) -> tuple[FaqSource, ...]:
    rows = read_csv_rows(path, required_columns=_SOURCE_COLUMNS)
    sources: list[FaqSource] = []
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        source_id = require_value(row, "SourceID", path=path, line=line)
        if source_id in seen:
            raise DatasetFormatError(
                path=path, reason=f"duplicate SourceID {source_id}"
            )
        seen.add(source_id)
        sources.append(
            FaqSource(
                source_id=source_id,
                description=require_value(row, "설명", path=path, line=line),
                url=require_value(row, "URL", path=path, line=line),
                note=row["비고"].strip(),
            )
        )
    return tuple(sources)


def load_faq_records(faq_path: Path, sources_path: Path) -> tuple[FaqRecord, ...]:
    """Load FAQ rows and validate every citation against the source registry."""
    source_ids = {source.source_id for source in _load_sources(sources_path)}
    rows = read_csv_rows(faq_path, required_columns=_FAQ_COLUMNS)
    records: list[FaqRecord] = []
    seen: set[int] = set()
    for line, row in enumerate(rows, start=2):
        raw_id = require_value(row, "ID", path=faq_path, line=line)
        if not raw_id.isdecimal():
            raise DatasetFormatError(path=faq_path, reason=f"non-numeric ID {raw_id}")
        faq_id = int(raw_id)
        if faq_id in seen:
            raise DatasetFormatError(path=faq_path, reason=f"duplicate ID {raw_id}")
        seen.add(faq_id)

        paraphrases = tuple(
            part.strip()
            for part in _PARAPHRASE_SEPARATOR.split(
                require_value(row, "유사질문표현", path=faq_path, line=line)
            )
            if part.strip()
        )
        facts = tuple(
            part.strip()
            for part in require_value(
                row, "AI분기포인트", path=faq_path, line=line
            ).split(",")
            if part.strip()
        )
        citations = tuple(
            part.strip()
            for part in require_value(row, "근거ID", path=faq_path, line=line).split(
                ","
            )
            if part.strip()
        )
        unknown = sorted(set(citations).difference(source_ids))
        if unknown:
            raise DatasetFormatError(
                path=faq_path,
                reason=f"unknown source IDs at row {line}: {', '.join(unknown)}",
            )
        records.append(
            FaqRecord(
                faq_id=faq_id,
                category=require_value(row, "카테고리", path=faq_path, line=line),
                representative_question=require_value(
                    row, "대표질문", path=faq_path, line=line
                ),
                paraphrases=paraphrases,
                gold_answer=require_value(row, "표준답변", path=faq_path, line=line),
                required_facts=facts,
                source_kind=require_value(row, "근거구분", path=faq_path, line=line),
                source_ids=citations,
            )
        )
    return tuple(records)


__all__ = ["DatasetFormatError", "FaqRecord", "FaqSource", "load_faq_records"]
