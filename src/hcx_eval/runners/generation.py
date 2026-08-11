"""Bounded generation planning, execution, failure retention, and resume."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, ClassVar, Protocol

from pydantic import BaseModel, ConfigDict, Field, JsonValue, TypeAdapter
from typing_extensions import override

from hcx_eval.artifacts.writer import SegmentedJsonlWriter
from hcx_eval.clients.base import ErrorKind, ProviderApiError
from hcx_eval.clients.native_v1 import NativeV1ChatRequest, NativeV1Client
from hcx_eval.clients.native_v3 import NativeV3ChatRequest, NativeV3Client
from hcx_eval.clients.openai_compat import (
    OpenAIChatRequest,
    OpenAICompatibleClient,
)
from hcx_eval.clients.types import ChatMessage
from hcx_eval.ids import RequestIdentity, make_request_id
from hcx_eval.schemas.case import (  # noqa: TC001 - Pydantic resolves at runtime.
    EvaluationCase,
)
from hcx_eval.schemas.model import ModelRecord, ModelStatus
from hcx_eval.schemas.results import ApiFamily, RawResult, Usage

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

_JSON_OBJECT = TypeAdapter(dict[str, JsonValue])
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
_RETRYABLE_KINDS = frozenset(
    {ErrorKind.RATE_LIMIT, ErrorKind.SERVER, ErrorKind.TIMEOUT}
)


@dataclass(frozen=True, slots=True)
class RequestPlanLimitError(ValueError):
    """A complete plan would exceed its explicit request ceiling."""

    planned: int
    ceiling: int

    @override
    def __str__(self) -> str:
        return f"planned {self.planned} requests exceeds ceiling {self.ceiling}"


class GenerationJob(BaseModel):
    """One deterministic model/case request."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    model: str = Field(min_length=1)
    api_family: ApiFamily
    case: EvaluationCase
    max_tokens: int = Field(gt=0)
    prompt_version: str = Field(default="finance_qa_v001", min_length=1)
    model_mode: str | None = None


class GenerationPlan(BaseModel):
    """Fully enumerated request plan proven to fit its ceiling."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    run_id: str = Field(min_length=1)
    max_requests: int = Field(gt=0)
    jobs: tuple[GenerationJob, ...]

    @property
    def request_count(self) -> int:
        """Return the exact number of dispatches before retry accounting."""
        return len(self.jobs)


class GenerationOutcome(BaseModel):
    """Adapter-neutral successful generation response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    text: str
    raw: JsonValue
    usage: Usage | None = None
    http_status: int = Field(default=200, ge=100, le=399)
    provider_status_code: str | None = None
    retry_count: int = Field(default=0, ge=0)


class GenerationBackend(Protocol):
    """Adapter router boundary used by mocked and live executors."""

    async def generate(self, job: GenerationJob) -> GenerationOutcome:
        """Generate one outcome using the job's explicit API family."""
        ...


@dataclass(frozen=True, slots=True)
class BackendConfigurationError(RuntimeError):
    """A planned API family has no separately configured adapter."""

    api_family: ApiFamily

    @override
    def __str__(self) -> str:
        return f"no generation adapter configured for {self.api_family.value}"


class AdapterGenerationBackend:
    """Route jobs without merging OpenAI-compatible, native v1, or native v3 wires."""

    _openai: OpenAICompatibleClient | None
    _native_v1: NativeV1Client | None
    _native_v3: NativeV3Client | None

    def __init__(
        self,
        *,
        openai: OpenAICompatibleClient | None = None,
        native_v1: NativeV1Client | None = None,
        native_v3: NativeV3Client | None = None,
    ) -> None:
        """Bind only explicitly configured protocol adapters."""
        self._openai = openai
        self._native_v1 = native_v1
        self._native_v3 = native_v3

    async def generate(self, job: GenerationJob) -> GenerationOutcome:
        """Execute one non-streaming job through its exact API contract."""
        messages = (ChatMessage(role="user", content=job.case.prompt),)
        match job.api_family:
            case ApiFamily.OPENAI_COMPAT:
                if self._openai is None:
                    raise BackendConfigurationError(job.api_family)
                response = await self._openai.chat(
                    OpenAIChatRequest(
                        model=job.model,
                        messages=messages,
                        max_tokens=job.max_tokens,
                    )
                )
                if not response.choices:
                    message = "compatible response contains no choices"
                    raise ValueError(message)
                return GenerationOutcome(
                    text=response.choices[0].message.content,
                    raw=response.model_dump(mode="json"),
                    usage=Usage(
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens,
                        total_tokens=response.usage.total_tokens,
                    ),
                )
            case ApiFamily.NATIVE_V1:
                if self._native_v1 is None:
                    raise BackendConfigurationError(job.api_family)
                response = await self._native_v1.chat(
                    NativeV1ChatRequest(
                        model=job.model,
                        messages=messages,
                        max_tokens=job.max_tokens,
                    )
                )
                usage = Usage(
                    prompt_tokens=response.result.input_length,
                    completion_tokens=response.result.output_length,
                    total_tokens=(
                        response.result.input_length + response.result.output_length
                    ),
                )
                return GenerationOutcome(
                    text=response.result.message.content,
                    raw=response.model_dump(mode="json"),
                    usage=usage,
                )
            case ApiFamily.NATIVE_V3:
                if self._native_v3 is None:
                    raise BackendConfigurationError(job.api_family)
                response = await self._native_v3.chat(
                    NativeV3ChatRequest(
                        model=job.model,
                        messages=messages,
                        max_tokens=job.max_tokens,
                    )
                )
                usage = response.result.usage
                return GenerationOutcome(
                    text=response.result.message.content,
                    raw=response.model_dump(mode="json"),
                    usage=Usage(
                        prompt_tokens=usage.prompt_tokens,
                        completion_tokens=usage.completion_tokens,
                        total_tokens=usage.total_tokens,
                    ),
                )
            case ApiFamily.API_TOOL:
                raise BackendConfigurationError(job.api_family)


class GenerationRunSummary(BaseModel):
    """Execution and resume counts for one plan invocation."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    run_id: str
    planned: int = Field(ge=0)
    executed: int = Field(ge=0)
    skipped: int = Field(ge=0)
    failed: int = Field(ge=0)


def _is_generation_model(model: ModelRecord) -> bool:
    if model.status is not ModelStatus.LIVE:
        return False
    supported = {
        capability.name
        for capability in model.capabilities
        if capability.supported is not False
    }
    return not supported or bool(supported.intersection(_GENERATION_CAPABILITIES))


def _api_family(model: ModelRecord) -> ApiFamily:
    if not model.api_families:
        return ApiFamily.OPENAI_COMPAT
    supported = tuple(
        ApiFamily(value)
        for value in model.api_families
        if value != ApiFamily.API_TOOL.value
    )
    if not supported:
        message = f"model {model.identifier} has no generation API family"
        raise ValueError(message)
    return supported[0]


def plan_generation(  # noqa: PLR0913 - explicit safety ceilings are call-site visible.
    cases: Sequence[EvaluationCase],
    registry: Sequence[ModelRecord],
    *,
    run_id: str,
    max_requests: int,
    max_tokens: int,
    phases: Sequence[str],
    model_selectors: Sequence[str],
) -> GenerationPlan:
    """Enumerate selected jobs and fail rather than truncate at the ceiling."""
    if max_requests <= 0 or max_tokens <= 0:
        message = "request and token ceilings must be positive"
        raise ValueError(message)
    registry_ids = {model.identifier for model in registry}
    selectors = set(model_selectors)
    if "all" not in selectors:
        unknown = sorted(selectors.difference(registry_ids))
        if unknown:
            message = f"unknown model selectors: {', '.join(unknown)}"
            raise ValueError(message)
    selected_models = tuple(
        sorted(
            (
                model
                for model in registry
                if _is_generation_model(model)
                and ("all" in selectors or model.identifier in selectors)
            ),
            key=lambda model: model.identifier,
        )
    )
    phase_set = set(phases)
    selected_cases = tuple(
        sorted(
            (case for case in cases if case.task in phase_set),
            key=lambda case: case.case_id,
        )
    )
    jobs = tuple(
        GenerationJob(
            model=model.identifier,
            api_family=_api_family(model),
            case=case,
            max_tokens=max_tokens,
        )
        for model in selected_models
        for case in selected_cases
    )
    if len(jobs) > max_requests:
        raise RequestPlanLimitError(planned=len(jobs), ceiling=max_requests)
    return GenerationPlan(run_id=run_id, max_requests=max_requests, jobs=jobs)


def _completed_request_ids(results_root: Path, run_id: str) -> set[str]:
    completed: set[str] = set()
    raw_root = results_root.resolve() / run_id / "raw"
    for path in sorted(raw_root.glob("segment-*.jsonl")):
        payload = path.read_bytes()
        if payload and not payload.endswith(b"\n"):
            continue
        for line in payload.splitlines():
            try:
                record = _JSON_OBJECT.validate_json(line)
            except ValueError:
                continue
            request_id = record.get("request_id")
            if isinstance(request_id, str) and request_id:
                completed.add(request_id)
    return completed


def _request_id(plan: GenerationPlan, job: GenerationJob) -> str:
    return make_request_id(
        RequestIdentity(
            run_id=plan.run_id,
            case_id=job.case.case_id,
            model=job.model,
            model_mode=job.model_mode,
            attempt=0,
        )
    )


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _failed_result(  # noqa: PLR0913 - immutable request evidence is explicit.
    *,
    plan: GenerationPlan,
    job: GenerationJob,
    request_id: str,
    started_at: datetime,
    e2e_ms: float,
    error: Exception,
    docs_snapshot_sha256: str,
) -> RawResult:
    if isinstance(error, ProviderApiError):
        raw: JsonValue = (
            None
            if error.response_body is None
            else {
                "sanitized_body": error.response_body.decode(
                    "utf-8", errors="backslashreplace"
                )
            }
        )
        kind = error.kind.value
        http_status = error.http_status
        provider_code = error.provider_code
        retryable = error.kind in _RETRYABLE_KINDS
    else:
        raw = None
        kind = "runner"
        http_status = None
        provider_code = None
        retryable = isinstance(error, TimeoutError)
    return RawResult.model_validate(
        {
            "run_id": plan.run_id,
            "request_id": request_id,
            "case_id": job.case.case_id,
            "model": job.model,
            "model_mode": job.model_mode,
            "api_family": job.api_family,
            "prompt_version": job.prompt_version,
            "dataset_sha256": job.case.dataset_sha256,
            "docs_snapshot_sha256": docs_snapshot_sha256,
            "request": {
                "payload": {
                    "model": job.model,
                    "prompt": job.case.prompt,
                    "max_tokens": job.max_tokens,
                }
            },
            "response_raw": raw,
            "timing": {"started_at": started_at, "e2e_ms": e2e_ms},
            "http_status": http_status,
            "provider_status_code": provider_code,
            "error": {
                "kind": kind,
                "message": str(error),
                "retryable": retryable,
                "provider_code": provider_code,
            },
        }
    )


async def execute_generation_plan(  # noqa: PLR0913 - clocks are test injection seams.
    plan: GenerationPlan,
    *,
    backend: GenerationBackend,
    results_root: Path,
    docs_snapshot_sha256: str,
    clock: Callable[[], float] = time.monotonic,
    now: Callable[[], datetime] = _utc_now,
) -> GenerationRunSummary:
    """Execute pending jobs once and append success or failure for every attempt."""
    writer = SegmentedJsonlWriter(results_root, plan.run_id)
    completed = _completed_request_ids(results_root, plan.run_id)
    executed = 0
    skipped = 0
    failed = 0
    for job in plan.jobs:
        request_id = _request_id(plan, job)
        if request_id in completed:
            skipped += 1
            continue
        started_at = now()
        started = clock()
        try:
            outcome = await backend.generate(job)
        except Exception as error:  # noqa: BLE001 - every failed request is evidence.
            elapsed = max((clock() - started) * 1000, 0.0)
            result = _failed_result(
                plan=plan,
                job=job,
                request_id=request_id,
                started_at=started_at,
                e2e_ms=elapsed,
                error=error,
                docs_snapshot_sha256=docs_snapshot_sha256,
            )
            failed += 1
        else:
            elapsed = max((clock() - started) * 1000, 0.0)
            result = RawResult.model_validate(
                {
                    "run_id": plan.run_id,
                    "request_id": request_id,
                    "case_id": job.case.case_id,
                    "model": job.model,
                    "model_mode": job.model_mode,
                    "api_family": job.api_family,
                    "prompt_version": job.prompt_version,
                    "dataset_sha256": job.case.dataset_sha256,
                    "docs_snapshot_sha256": docs_snapshot_sha256,
                    "request": {
                        "payload": {
                            "model": job.model,
                            "prompt": job.case.prompt,
                            "max_tokens": job.max_tokens,
                        }
                    },
                    "response_raw": outcome.raw,
                    "response_text": outcome.text,
                    "timing": {"started_at": started_at, "e2e_ms": elapsed},
                    "usage": outcome.usage,
                    "http_status": outcome.http_status,
                    "provider_status_code": outcome.provider_status_code,
                    "retry_count": outcome.retry_count,
                }
            )
        _ = writer.append(result)
        executed += 1
    return GenerationRunSummary(
        run_id=plan.run_id,
        planned=plan.request_count,
        executed=executed,
        skipped=skipped,
        failed=failed,
    )
