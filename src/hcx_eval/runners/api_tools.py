"""Isolated API-tool quality-gain and incremental-latency evaluation."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, Protocol

from pydantic import BaseModel, ConfigDict, Field, JsonValue

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence


class ApiToolName(StrEnum):
    """Documented tool families evaluated as separate pipeline stages."""

    RERANKER = "reranker"
    RAG_REASONING = "rag-reasoning"
    ROUTER = "router"
    SUMMARIZATION = "summarization"
    SEGMENTATION = "segmentation"
    SLIDING_WINDOW = "sliding-window"
    TOKENIZER = "tokenizer"
    SKILLSET = "skillset"


class ApiToolCase(BaseModel):
    """One reviewed tool input with an existing pipeline baseline."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    case_id: str = Field(min_length=1)
    payload: JsonValue
    expected: JsonValue
    baseline_quality: float = Field(ge=0, le=1)
    baseline_latency_ms: float = Field(ge=0)


class ApiToolOutcome(BaseModel):
    """One tool output and its standalone client latency."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    output: JsonValue
    latency_ms: float = Field(ge=0)


class ApiToolBackend(Protocol):
    """Injected boundary for independently callable API tools."""

    def invoke(
        self,
        tool: ApiToolName,
        case: ApiToolCase,
    ) -> Awaitable[ApiToolOutcome]:
        """Invoke exactly one tool for one case."""
        ...


class ApiToolResult(BaseModel):
    """Baseline-versus-tool quality and latency comparison."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    case_id: str
    tool: ApiToolName
    baseline_quality: float = Field(ge=0, le=1)
    tool_quality: float = Field(ge=0, le=1)
    quality_gain: float = Field(ge=-1, le=1)
    baseline_latency_ms: float = Field(ge=0)
    added_latency_ms: float = Field(ge=0)
    end_to_end_latency_ms: float = Field(ge=0)


async def evaluate_api_tools(
    cases: Sequence[ApiToolCase],
    tools: Sequence[ApiToolName],
    *,
    backend: ApiToolBackend,
    scorer: Callable[[JsonValue, JsonValue], float],
    max_requests: int,
) -> tuple[ApiToolResult, ...]:
    """Evaluate each requested tool independently under a hard request ceiling."""
    if max_requests <= 0:
        message = "API-tool request ceiling must be positive"
        raise ValueError(message)
    planned = len(cases) * len(tools)
    if planned > max_requests:
        message = f"planned {planned} requests exceeds ceiling {max_requests}"
        raise ValueError(message)
    results: list[ApiToolResult] = []
    for tool in tools:
        for case in cases:
            outcome = await backend.invoke(tool, case)
            quality = scorer(outcome.output, case.expected)
            if not 0 <= quality <= 1:
                message = "tool scorer must return a value between zero and one"
                raise ValueError(message)
            results.append(
                ApiToolResult(
                    case_id=case.case_id,
                    tool=tool,
                    baseline_quality=case.baseline_quality,
                    tool_quality=quality,
                    quality_gain=quality - case.baseline_quality,
                    baseline_latency_ms=case.baseline_latency_ms,
                    added_latency_ms=outcome.latency_ms,
                    end_to_end_latency_ms=(
                        case.baseline_latency_ms + outcome.latency_ms
                    ),
                )
            )
    return tuple(results)
