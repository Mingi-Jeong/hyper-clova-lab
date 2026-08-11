"""Offline-only request accounting for specialized benchmark phases."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from hcx_eval.runners.embeddings import build_retrieval_benchmark
from hcx_eval.schemas.model import ModelStatus
from hcx_eval.schemas.results import ApiFamily

if TYPE_CHECKING:
    from collections.abc import Sequence

    from hcx_eval.schemas.case import EvaluationCase
    from hcx_eval.schemas.model import ModelRecord

_GENERATION_CAPABILITIES = frozenset(
    {
        "chat",
        "function_calling",
        "generation",
        "structured_outputs",
        "text",
        "thinking",
        "vision",
    }
)


class SpecializedPhase(StrEnum):
    """Phases whose runner has its own non-baseline wire behavior."""

    LATENCY = "latency"
    EMBEDDINGS = "embeddings"
    API_TOOLS = "api-tools"
    SAFETY = "safety"


class SpecializedPreflight(BaseModel):
    """Exact offline plan summary with no executable network object."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    phases: tuple[SpecializedPhase, ...]
    models: tuple[str, ...]
    request_count: int = Field(ge=0)
    max_requests: int = Field(gt=0)


def _selected_models(
    registry: Sequence[ModelRecord],
    selectors: Sequence[str],
) -> tuple[ModelRecord, ...]:
    registry_ids = {model.identifier for model in registry}
    selected = set(selectors)
    if "all" not in selected:
        unknown = sorted(selected.difference(registry_ids))
        if unknown:
            message = f"unknown model selectors: {', '.join(unknown)}"
            raise ValueError(message)
    return tuple(
        model
        for model in registry
        if model.status is ModelStatus.LIVE
        and ("all" in selected or model.identifier in selected)
    )


def _generation_models(models: Sequence[ModelRecord]) -> tuple[ModelRecord, ...]:
    selected: list[ModelRecord] = []
    for model in models:
        supported = {
            capability.name
            for capability in model.capabilities
            if capability.supported is not False
        }
        if not supported or supported.intersection(_GENERATION_CAPABILITIES):
            selected.append(model)
    return tuple(selected)


def plan_specialized_phases(  # noqa: PLR0913 - all expansion factors are explicit.
    cases: Sequence[EvaluationCase],
    registry: Sequence[ModelRecord],
    *,
    phases: Sequence[str],
    model_selectors: Sequence[str],
    max_requests: int,
    latency_warmups: int,
    latency_samples: int,
    safety_case_count: int,
) -> SpecializedPreflight:
    """Count every specialized request and fail rather than truncate."""
    if max_requests <= 0:
        message = "specialized request ceiling must be positive"
        raise ValueError(message)
    if latency_warmups < 0 or latency_samples <= 0 or safety_case_count <= 0:
        message = "specialized phase expansion factors are invalid"
        raise ValueError(message)
    try:
        selected_phases = tuple(SpecializedPhase(phase) for phase in phases)
    except ValueError as error:
        message = "specialized phases cannot be mixed with generation tasks"
        raise ValueError(message) from error
    if len(selected_phases) != len(set(selected_phases)):
        message = "specialized phases must be unique"
        raise ValueError(message)
    models = _selected_models(registry, model_selectors)
    generation_models = _generation_models(models)
    benchmark = build_retrieval_benchmark(cases)
    embedding_inputs = len(benchmark.documents) + len(benchmark.examples)
    embedding_models = tuple(
        model
        for model in models
        if any(
            capability.name == "embedding" and capability.supported is not False
            for capability in model.capabilities
        )
    )
    api_tools = tuple(
        model for model in models if ApiFamily.API_TOOL.value in model.api_families
    )
    counts = {
        SpecializedPhase.LATENCY: len(generation_models)
        * (latency_warmups + latency_samples),
        SpecializedPhase.EMBEDDINGS: len(embedding_models) * embedding_inputs,
        SpecializedPhase.API_TOOLS: len(api_tools),
        SpecializedPhase.SAFETY: len(generation_models) * safety_case_count,
    }
    request_count = sum(counts[phase] for phase in selected_phases)
    if request_count > max_requests:
        message = f"planned {request_count} requests exceeds ceiling {max_requests}"
        raise ValueError(message)
    involved = {
        model.identifier
        for model_group in (generation_models, embedding_models, api_tools)
        for model in model_group
    }
    return SpecializedPreflight(
        phases=selected_phases,
        models=tuple(sorted(involved)),
        request_count=request_count,
        max_requests=max_requests,
    )
