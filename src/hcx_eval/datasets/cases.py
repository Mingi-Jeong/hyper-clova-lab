"""Deterministic structured-case construction and conflict-safe output."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path  # noqa: TC003 - Pydantic resolves Path at runtime.
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import override

from hcx_eval.datasets.faq import FaqRecord, load_faq_records
from hcx_eval.datasets.inventory import build_inventory
from hcx_eval.datasets.transfer_codes import TransferReason, load_transfer_reasons
from hcx_eval.schemas.case import EvaluationCase

_DEVELOPMENT_PERCENT = 20
_VALIDATION_PERCENT = 40


class StructuredCaseBundle(BaseModel):
    """One reproducible set of structured cases and its content identities."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    source_root: Path
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    cases_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    cases: tuple[EvaluationCase, ...]


class CaseWriteSummary(BaseModel):
    """Secret-free summary of a generated JSONL case artifact."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    output: Path
    case_count: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class CaseOutputConflictError(RuntimeError):
    """Generated cases would overwrite different bytes or protected input."""

    path: Path
    reason: str

    @override
    def __str__(self) -> str:
        return f"cannot write case bundle {self.path}: {self.reason}"


def _split(group_id: str) -> str:
    bucket = int(hashlib.sha256(group_id.encode()).hexdigest()[:8], 16) % 100
    if bucket < _DEVELOPMENT_PERCENT:
        return "development"
    if bucket < _VALIDATION_PERCENT:
        return "validation"
    return "test"


def _faq_cases(record: FaqRecord, dataset_sha256: str) -> tuple[EvaluationCase, ...]:
    group_id = f"FAQ-{record.faq_id:04d}"
    split = _split(group_id)
    expected = {
        "answer": record.gold_answer,
        "required_facts": list(record.required_facts),
        "gold_source_ids": list(record.source_ids),
        "answerable": True,
    }
    common_metadata = {
        "category": record.category,
        "group_id": group_id,
        "split": split,
        "source_kind": record.source_kind,
    }
    cases = [
        EvaluationCase.model_validate(
            {
                "case_id": f"{group_id}-R",
                "task": "default_option_qa",
                "prompt": record.representative_question,
                "expected": expected,
                "source_ids": record.source_ids,
                "dataset_sha256": dataset_sha256,
                "metadata": {
                    **common_metadata,
                    "variant": "representative",
                    "review_status": "source_verified",
                },
            },
        )
    ]
    cases.extend(
        EvaluationCase.model_validate(
            {
                "case_id": f"{group_id}-P{index}",
                "task": "default_option_qa",
                "prompt": paraphrase,
                "expected": expected,
                "source_ids": record.source_ids,
                "dataset_sha256": dataset_sha256,
                "metadata": {
                    **common_metadata,
                    "variant": f"paraphrase-{index}",
                    "review_status": "unreviewed",
                },
            },
        )
        for index, paraphrase in enumerate(record.paraphrases, start=1)
    )
    return tuple(cases)


def _transfer_cases(
    record: TransferReason,
    dataset_sha256: str,
) -> tuple[EvaluationCase, EvaluationCase]:
    group_id = f"TRANSFER-{record.code}"
    split = _split(group_id)
    source_ids = (f"in_kind_transfer_restriction_reasons.csv#{record.code}",)
    metadata = {
        "group_id": group_id,
        "split": split,
        "review_status": "source_verified",
    }
    expected = {
        "code": record.code,
        "reason_name": record.reason_name,
        "description": record.description,
    }
    return (
        EvaluationCase.model_validate(
            {
                "case_id": f"{group_id}-CODE-TO-REASON",
                "task": "transfer_code_to_reason",
                "prompt": "".join(
                    (
                        f"실물이전 제한 코드 {record.code}의 불가 사유명과 설명을 ",
                        "답하세요.",
                    )
                ),
                "expected": expected,
                "source_ids": source_ids,
                "dataset_sha256": dataset_sha256,
                "metadata": {**metadata, "direction": "code-to-reason"},
            }
        ),
        EvaluationCase.model_validate(
            {
                "case_id": f"{group_id}-REASON-TO-CODE",
                "task": "transfer_reason_to_code",
                "prompt": "".join(
                    (
                        "다음 실물이전 불가 사유에 해당하는 두 자리 코드를 답하세요: ",
                        f"{record.reason_name}. {record.description}",
                    )
                ),
                "expected": expected,
                "source_ids": source_ids,
                "dataset_sha256": dataset_sha256,
                "metadata": {**metadata, "direction": "reason-to-code"},
            }
        ),
    )


def _case_bytes(cases: tuple[EvaluationCase, ...]) -> bytes:
    lines = (
        json.dumps(
            case.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        for case in cases
    )
    return ("\n".join(lines) + ("\n" if cases else "")).encode()


def build_structured_cases(data_root: Path) -> StructuredCaseBundle:
    """Build versioned FAQ and transfer-code cases from protected CSV inputs."""
    resolved_root = data_root.resolve()
    datasets = resolved_root / "datasets"
    inventory = build_inventory(datasets)
    faq_records = load_faq_records(
        datasets / "default_option_faq_100.csv",
        datasets / "default_option_sources.csv",
    )
    transfer_records = load_transfer_reasons(
        datasets / "in_kind_transfer_restriction_reasons.csv"
    )
    cases = tuple(
        sorted(
            (
                case
                for record in faq_records
                for case in _faq_cases(record, inventory.sha256)
            ),
            key=lambda case: case.case_id,
        )
    ) + tuple(
        sorted(
            (
                case
                for record in transfer_records
                for case in _transfer_cases(record, inventory.sha256)
            ),
            key=lambda case: case.case_id,
        )
    )
    if len({case.case_id for case in cases}) != len(cases):
        message = "generated duplicate case IDs"
        raise ValueError(message)
    content = _case_bytes(cases)
    return StructuredCaseBundle(
        source_root=resolved_root,
        dataset_sha256=inventory.sha256,
        cases_sha256=hashlib.sha256(content).hexdigest(),
        cases=cases,
    )


def write_case_bundle(
    bundle: StructuredCaseBundle,
    output: Path,
) -> CaseWriteSummary:
    """Write once, or accept only an existing byte-identical JSONL artifact."""
    resolved_output = output.resolve()
    if resolved_output.is_relative_to(bundle.source_root):
        raise CaseOutputConflictError(
            path=output,
            reason="output is inside protected source root",
        )
    content = _case_bytes(bundle.cases)
    digest = hashlib.sha256(content).hexdigest()
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with resolved_output.open("xb") as target:
            _ = target.write(content)
            target.flush()
            os.fsync(target.fileno())
    except FileExistsError:
        if resolved_output.read_bytes() != content:
            raise CaseOutputConflictError(
                path=output,
                reason="different artifact already exists",
            ) from None
    return CaseWriteSummary(
        output=resolved_output,
        case_count=len(bundle.cases),
        sha256=digest,
    )
