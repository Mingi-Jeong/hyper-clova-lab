from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from hcx_eval.runners.embeddings import (
    EmbeddingDimensionError,
    EmbeddingOutcome,
    build_retrieval_benchmark,
    plan_embeddings,
    run_embedding_plan,
)
from hcx_eval.schemas.case import EvaluationCase
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus

if TYPE_CHECKING:
    from collections.abc import Mapping


def _case(
    case_id: str,
    question: str,
    answer: str,
    *,
    review_status: str = "source_verified",
) -> EvaluationCase:
    return EvaluationCase.model_validate(
        {
            "case_id": case_id,
            "task": "default_option_qa",
            "prompt": question,
            "expected": {"answer": answer},
            "source_ids": ["S1"],
            "dataset_sha256": "a" * 64,
            "metadata": {"review_status": review_status, "split": "test"},
        }
    )


def _embedding_model() -> ModelRecord:
    return ModelRecord(
        identifier="bge-m3",
        status=ModelStatus.LIVE,
        api_families=("openai-compatible",),
        capabilities=(Capability(name="embedding", supported=True),),
        evidence=("fixture",),
    )


class FixtureEmbeddingBackend:
    vectors: Mapping[str, tuple[float, ...]]

    def __init__(self, vectors: Mapping[str, tuple[float, ...]]) -> None:
        self.vectors = vectors
        self.calls: list[tuple[str, str]] = []

    async def embed(self, model: str, text: str) -> EmbeddingOutcome:
        self.calls.append((model, text))
        return EmbeddingOutcome(vector=self.vectors[text], latency_ms=1.0)


@pytest.mark.anyio
async def test_embedding_runner_scores_reviewed_retrieval_and_dimensions() -> None:
    cases = (
        _case("FAQ-0001-R", "q1", "d1"),
        _case("FAQ-0002-R", "q2", "d2"),
    )
    benchmark = build_retrieval_benchmark(cases)
    plan = plan_embeddings(
        benchmark,
        (_embedding_model(),),
        max_requests=4,
        max_input_chars=10,
    )
    backend = FixtureEmbeddingBackend(
        {"q1": (1.0, 0.0), "d1": (1.0, 0.0), "q2": (0.0, 1.0), "d2": (0.0, 1.0)}
    )

    results = await run_embedding_plan(plan, backend)

    assert plan.request_count == 4
    assert len(backend.calls) == 4
    assert len(results) == 1
    assert results[0].dimension == 2
    assert results[0].recall_at_1 == 1.0
    assert results[0].mrr == 1.0
    assert results[0].ndcg == 1.0


@pytest.mark.anyio
async def test_embedding_runner_rejects_dimension_drift() -> None:
    cases = (
        _case("FAQ-0001-R", "q1", "d1"),
        _case("FAQ-0002-R", "q2", "d2"),
    )
    plan = plan_embeddings(
        build_retrieval_benchmark(cases),
        (_embedding_model(),),
        max_requests=4,
        max_input_chars=10,
    )
    backend = FixtureEmbeddingBackend(
        {"q1": (1.0, 0.0), "d1": (1.0, 0.0), "q2": (0.0, 1.0), "d2": (0.0, 1.0, 2.0)}
    )

    with pytest.raises(EmbeddingDimensionError, match="dimension drift"):
        _ = await run_embedding_plan(plan, backend)


def test_embedding_plan_rejects_unreviewed_and_oversized_inputs() -> None:
    reviewed = _case("FAQ-0001-R", "q1", "d1")
    unreviewed = _case(
        "FAQ-0001-P1",
        "q1 paraphrase",
        "d1",
        review_status="unreviewed",
    )
    benchmark = build_retrieval_benchmark((reviewed, unreviewed))
    assert len(benchmark.examples) == 1

    with pytest.raises(ValueError, match="input limit"):
        _ = plan_embeddings(
            benchmark,
            (_embedding_model(),),
            max_requests=2,
            max_input_chars=1,
        )
