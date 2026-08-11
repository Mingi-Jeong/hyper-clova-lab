"""Minimal one-request-per-live-generation-model smoke planning."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hcx_eval.runners.generation import GenerationPlan, plan_generation
from hcx_eval.schemas.case import EvaluationCase

if TYPE_CHECKING:
    from collections.abc import Sequence

    from hcx_eval.schemas.model import ModelRecord


def plan_smoke(
    registry: Sequence[ModelRecord],
    *,
    run_id: str,
    dataset_sha256: str,
    max_requests: int,
    max_tokens: int,
) -> GenerationPlan:
    """Plan one bounded synthetic Korean prompt per live generation model."""
    case = EvaluationCase.model_validate(
        {
            "case_id": "SMOKE-TEXT-0001",
            "task": "smoke",
            "prompt": "한 문장으로 연결 상태를 확인해 주세요.",
            "expected": {"criterion": "non-empty Korean response"},
            "source_ids": ["synthetic:smoke"],
            "dataset_sha256": dataset_sha256,
            "metadata": {
                "split": "smoke",
                "review_status": "synthetic_reviewed",
            },
        }
    )
    return plan_generation(
        (case,),
        registry,
        run_id=run_id,
        max_requests=max_requests,
        max_tokens=max_tokens,
        phases=("smoke",),
        model_selectors=("all",),
    )
