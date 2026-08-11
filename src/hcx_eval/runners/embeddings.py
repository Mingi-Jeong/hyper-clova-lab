"""Reviewed-case embedding retrieval planning and deterministic evaluation."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Protocol

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import override

from hcx_eval.clients.openai_compat import (
    OpenAICompatibleClient,
    OpenAIEmbeddingRequest,
)
from hcx_eval.metrics.latency import percentile
from hcx_eval.metrics.retrieval import ndcg_at_k, recall_at_k, reciprocal_rank
from hcx_eval.schemas.model import ModelRecord, ModelStatus

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from hcx_eval.schemas.case import EvaluationCase


class RetrievalDocument(BaseModel):
    """One answer-backed corpus document."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    document_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class RetrievalExample(BaseModel):
    """One query and its relevant document identifier."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    case_id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    relevant_document_id: str = Field(min_length=1)


class RetrievalBenchmark(BaseModel):
    """Reviewed query set and deduplicated corpus."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    examples: tuple[RetrievalExample, ...]
    documents: tuple[RetrievalDocument, ...]


class EmbeddingOutcome(BaseModel):
    """One vector and client-measured call latency."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    vector: tuple[float, ...] = Field(min_length=1)
    latency_ms: float = Field(ge=0)


class EmbeddingBackend(Protocol):
    """Injected embedding adapter boundary."""

    async def embed(self, model: str, text: str) -> EmbeddingOutcome:
        """Embed one input through an explicit model."""
        ...


class OpenAIEmbeddingBackend:
    """Concrete OpenAI-compatible embedding adapter with client-clock latency."""

    _client: OpenAICompatibleClient
    _clock: Callable[[], float]

    def __init__(
        self,
        client: OpenAICompatibleClient,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Bind an already budgeted compatible client."""
        self._client = client
        self._clock = clock

    async def embed(self, model: str, text: str) -> EmbeddingOutcome:
        """Call the compatible float-vector endpoint exactly once."""
        started = self._clock()
        response = await self._client.embed(
            OpenAIEmbeddingRequest(model=model, input=text)
        )
        elapsed_ms = max((self._clock() - started) * 1000, 0.0)
        if not response.data:
            message = "embedding response contains no vectors"
            raise ValueError(message)
        return EmbeddingOutcome(
            vector=response.data[0].embedding,
            latency_ms=elapsed_ms,
        )


class EmbeddingPlan(BaseModel):
    """Bounded models and benchmark inputs."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    models: tuple[str, ...]
    benchmark: RetrievalBenchmark
    max_requests: int = Field(gt=0)
    max_input_chars: int = Field(gt=0)

    @property
    def request_count(self) -> int:
        """Return document plus query calls across all selected models."""
        inputs = len(self.benchmark.documents) + len(self.benchmark.examples)
        return len(self.models) * inputs


class EmbeddingScore(BaseModel):
    """Per-model retrieval, dimensionality, and latency scorecard."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    model: str
    request_count: int = Field(ge=0)
    dimension: int = Field(gt=0)
    recall_at_1: float = Field(ge=0, le=1)
    mrr: float = Field(ge=0, le=1)
    ndcg: float = Field(ge=0, le=1)
    latency_p50_ms: float = Field(ge=0)
    latency_p95_ms: float = Field(ge=0)


@dataclass(frozen=True, slots=True)
class EmbeddingPlanLimitError(ValueError):
    """Embedding inputs exceed the approved request ceiling."""

    planned: int
    ceiling: int

    @override
    def __str__(self) -> str:
        return f"planned {self.planned} requests exceeds ceiling {self.ceiling}"


@dataclass(frozen=True, slots=True)
class EmbeddingDimensionError(ValueError):
    """One model returned inconsistent vector dimensions."""

    model: str
    expected: int
    actual: int

    @override
    def __str__(self) -> str:
        prefix = f"embedding dimension drift for {self.model}"
        return f"{prefix}: expected {self.expected}, received {self.actual}"


class _EmbeddingCollector:
    """Per-model dimension and latency validation state."""

    _backend: EmbeddingBackend
    _model: str
    dimension: int | None
    latencies: list[float]

    def __init__(self, backend: EmbeddingBackend, model: str) -> None:
        self._backend = backend
        self._model = model
        self.dimension = None
        self.latencies = []

    async def embed(self, text: str) -> tuple[float, ...]:
        """Embed and reject dimension drift within one model."""
        outcome = await self._backend.embed(self._model, text)
        actual = len(outcome.vector)
        if self.dimension is None:
            self.dimension = actual
        elif actual != self.dimension:
            raise EmbeddingDimensionError(
                model=self._model,
                expected=self.dimension,
                actual=actual,
            )
        self.latencies.append(outcome.latency_ms)
        return outcome.vector


def build_retrieval_benchmark(
    cases: Sequence[EvaluationCase],
) -> RetrievalBenchmark:
    """Create query/answer retrieval pairs from source-verified cases only."""
    examples: list[RetrievalExample] = []
    documents: list[RetrievalDocument] = []
    for case in sorted(cases, key=lambda item: item.case_id):
        metadata = case.metadata.to_json()
        expected = case.expected.to_json()
        if not isinstance(expected, dict):
            continue
        if metadata.get("review_status") not in {
            "expert_verified",
            "reviewed",
            "source_verified",
            "synthetic_reviewed",
        }:
            continue
        answer = expected.get("answer")
        if not isinstance(answer, str) or not answer:
            continue
        documents.append(RetrievalDocument(document_id=case.case_id, text=answer))
        examples.append(
            RetrievalExample(
                case_id=case.case_id,
                query=case.prompt,
                relevant_document_id=case.case_id,
            )
        )
    return RetrievalBenchmark(examples=tuple(examples), documents=tuple(documents))


def _is_embedding_model(model: ModelRecord) -> bool:
    return model.status is ModelStatus.LIVE and any(
        capability.name == "embedding" and capability.supported is not False
        for capability in model.capabilities
    )


def plan_embeddings(
    benchmark: RetrievalBenchmark,
    registry: Sequence[ModelRecord],
    *,
    max_requests: int,
    max_input_chars: int,
) -> EmbeddingPlan:
    """Validate model status, input length, and complete request count."""
    if max_requests <= 0 or max_input_chars <= 0:
        message = "embedding request and input limits must be positive"
        raise ValueError(message)
    texts = tuple(document.text for document in benchmark.documents) + tuple(
        example.query for example in benchmark.examples
    )
    if any(len(text) > max_input_chars for text in texts):
        message = f"embedding input limit {max_input_chars} characters exceeded"
        raise ValueError(message)
    models = tuple(
        sorted(model.identifier for model in registry if _is_embedding_model(model))
    )
    plan = EmbeddingPlan(
        models=models,
        benchmark=benchmark,
        max_requests=max_requests,
        max_input_chars=max_input_chars,
    )
    if plan.request_count > max_requests:
        raise EmbeddingPlanLimitError(
            planned=plan.request_count,
            ceiling=max_requests,
        )
    return plan


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    numerator = sum(one * two for one, two in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


async def run_embedding_plan(
    plan: EmbeddingPlan,
    backend: EmbeddingBackend,
) -> tuple[EmbeddingScore, ...]:
    """Embed each unique input once per model and score deterministic retrieval."""
    scores: list[EmbeddingScore] = []
    for model in plan.models:
        collector = _EmbeddingCollector(backend, model)
        document_vectors: dict[str, tuple[float, ...]] = {}

        for document in plan.benchmark.documents:
            document_vectors[document.document_id] = await collector.embed(
                document.text
            )

        recalls: list[float] = []
        reciprocal_ranks: list[float] = []
        ndcgs: list[float] = []
        for example in plan.benchmark.examples:
            query_vector = await collector.embed(example.query)
            ranked = tuple(
                identifier
                for identifier, _ in sorted(
                    (
                        (identifier, _cosine(query_vector, vector))
                        for identifier, vector in document_vectors.items()
                    ),
                    key=lambda item: (-item[1], item[0]),
                )
            )
            relevant = (example.relevant_document_id,)
            recalls.append(recall_at_k(ranked, relevant, k=1))
            reciprocal_ranks.append(reciprocal_rank(ranked, relevant, k=len(ranked)))
            ndcgs.append(ndcg_at_k(ranked, relevant, k=len(ranked)))
        if collector.dimension is None or not collector.latencies or not recalls:
            message = "embedding plan contains no scorable inputs"
            raise ValueError(message)
        scores.append(
            EmbeddingScore(
                model=model,
                request_count=len(collector.latencies),
                dimension=collector.dimension,
                recall_at_1=sum(recalls) / len(recalls),
                mrr=sum(reciprocal_ranks) / len(reciprocal_ranks),
                ndcg=sum(ndcgs) / len(ndcgs),
                latency_p50_ms=percentile(tuple(collector.latencies), 0.50),
                latency_p95_ms=percentile(tuple(collector.latencies), 0.95),
            )
        )
    return tuple(scores)
