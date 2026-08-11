"""Isolated capability-specific planning with reviewed fixture validation."""

from __future__ import annotations

import hashlib
from enum import StrEnum
from pathlib import Path  # noqa: TC003 - Pydantic resolves Path at runtime.
from typing import TYPE_CHECKING, ClassVar, Protocol, Self

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    TypeAdapter,
    model_validator,
)

from hcx_eval.clients.base import ProviderApiError
from hcx_eval.schemas.model import ModelRecord, ModelStatus
from hcx_eval.security import redact_text

if TYPE_CHECKING:
    from collections.abc import Awaitable

_YAML_MAPPING = TypeAdapter(dict[str, JsonValue])


class CapabilityTrack(StrEnum):
    """Generation capability isolated into one request shape."""

    THINKING = "thinking"
    STRUCTURED_OUTPUTS = "structured_outputs"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    CONTEXT_LIMIT = "context_limit"


class CapabilityCellStatus(StrEnum):
    """Whether a capability cell may be dispatched."""

    PLANNED = "planned"
    UNSUPPORTED = "unsupported"


class ThinkingEffort(StrEnum):
    """Documented HCX-007 thinking effort levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolDefinition(BaseModel):
    """One deterministic function-calling tool contract."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    parameters: JsonValue


class VisionFixture(BaseModel):
    """Hash-pinned reviewed PNG without copying or changing protected input."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    case_id: str = Field(min_length=1)
    source_path: Path
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    media_type: str
    review_status: str
    prompt: str = Field(min_length=1)


class CapabilityCell(BaseModel):
    """One isolated request or evidence-only unsupported cell."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    cell_id: str = Field(min_length=1)
    model: str = Field(min_length=1)
    track: CapabilityTrack
    status: CapabilityCellStatus
    prompt: str = Field(min_length=1)
    thinking_effort: ThinkingEffort | None = None
    response_schema: JsonValue | None = None
    tools: tuple[ToolDefinition, ...] = ()
    vision_fixture: VisionFixture | None = None
    estimated_input_tokens: int | None = Field(default=None, gt=0)
    context_limit: int | None = Field(default=None, gt=0)
    reason: str | None = None

    @model_validator(mode="after")
    def enforce_isolated_wire_shape(self) -> Self:
        """Reject every prohibited cross-capability request combination."""
        extras = sum(
            (
                self.thinking_effort is not None,
                self.response_schema is not None,
                bool(self.tools),
                self.vision_fixture is not None,
            )
        )
        if self.status is CapabilityCellStatus.UNSUPPORTED:
            if self.reason is None:
                message = "unsupported capability cells require a reason"
                raise ValueError(message)
            return self
        if self.reason is not None:
            message = "planned capability cells cannot include a failure reason"
            raise ValueError(message)
        if self.track is CapabilityTrack.THINKING:
            valid = self.thinking_effort is not None and extras == 1
        elif self.track is CapabilityTrack.STRUCTURED_OUTPUTS:
            valid = self.response_schema is not None and extras == 1
        elif self.track is CapabilityTrack.FUNCTION_CALLING:
            valid = bool(self.tools) and extras == 1
        elif self.track is CapabilityTrack.VISION:
            valid = self.vision_fixture is not None and extras == 1
        else:
            valid = (
                extras == 0
                and self.estimated_input_tokens is not None
                and self.context_limit is not None
            )
        if not valid:
            message = f"{self.track.value} cannot be combined with another capability"
            raise ValueError(message)
        return self


class CapabilityPlan(BaseModel):
    """Bounded isolated capability cells."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    max_requests: int = Field(gt=0)
    cells: tuple[CapabilityCell, ...]

    @property
    def request_count(self) -> int:
        """Count only dispatchable cells; unsupported evidence costs no request."""
        return sum(cell.status is CapabilityCellStatus.PLANNED for cell in self.cells)


class CapabilityOutcome(BaseModel):
    """One successful isolated capability response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    output: JsonValue
    latency_ms: float = Field(ge=0)


class CapabilityBackend(Protocol):
    """Injected isolated capability-call boundary."""

    def __call__(self, cell: CapabilityCell) -> Awaitable[CapabilityOutcome]:
        """Invoke one planned capability cell."""
        ...


class CapabilityResultStatus(StrEnum):
    """Observed support outcome for one capability cell."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


class CapabilityResult(BaseModel):
    """Result or evidence-only unsupported capability cell."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    cell_id: str
    model: str
    track: CapabilityTrack
    status: CapabilityResultStatus
    output: JsonValue = None
    latency_ms: float | None = Field(default=None, ge=0)
    provider_code: str | None = None
    error: str | None = None


def _supported(model: ModelRecord, capability_name: str) -> bool:
    return model.status is ModelStatus.LIVE and any(
        capability.name == capability_name
        and capability.supported is True
        and "probe:supported" in capability.evidence
        for capability in model.capabilities
    )


def _unsupported(
    model: ModelRecord,
    track: CapabilityTrack,
    prompt: str,
) -> CapabilityCell:
    return CapabilityCell(
        cell_id=f"{model.identifier}-{track.value}-unsupported",
        model=model.identifier,
        track=track,
        status=CapabilityCellStatus.UNSUPPORTED,
        prompt=prompt,
        reason="live capability probe did not confirm support",
    )


def _plan(
    cells: tuple[CapabilityCell, ...],
    *,
    max_requests: int,
) -> CapabilityPlan:
    if max_requests <= 0:
        message = "capability request ceiling must be positive"
        raise ValueError(message)
    plan = CapabilityPlan(max_requests=max_requests, cells=cells)
    if plan.request_count > max_requests:
        message = (
            f"planned {plan.request_count} requests exceeds ceiling {max_requests}"
        )
        raise ValueError(message)
    return plan


def plan_thinking(
    model: ModelRecord,
    *,
    prompt: str,
    max_requests: int,
) -> CapabilityPlan:
    """Plan none/low/medium/high as four separate HCX-007 requests."""
    if not _supported(model, CapabilityTrack.THINKING.value):
        return _plan(
            (_unsupported(model, CapabilityTrack.THINKING, prompt),),
            max_requests=max_requests,
        )
    cells = tuple(
        CapabilityCell(
            cell_id=f"{model.identifier}-thinking-{effort.value}",
            model=model.identifier,
            track=CapabilityTrack.THINKING,
            status=CapabilityCellStatus.PLANNED,
            prompt=prompt,
            thinking_effort=effort,
        )
        for effort in ThinkingEffort
    )
    return _plan(cells, max_requests=max_requests)


def plan_structured_output(
    model: ModelRecord,
    *,
    prompt: str,
    response_schema: JsonValue,
    max_requests: int,
) -> CapabilityPlan:
    """Plan Structured Outputs without Thinking or tools."""
    track = CapabilityTrack.STRUCTURED_OUTPUTS
    if not _supported(model, track.value):
        return _plan((_unsupported(model, track, prompt),), max_requests=max_requests)
    cell = CapabilityCell(
        cell_id=f"{model.identifier}-structured-outputs",
        model=model.identifier,
        track=track,
        status=CapabilityCellStatus.PLANNED,
        prompt=prompt,
        response_schema=response_schema,
    )
    return _plan((cell,), max_requests=max_requests)


def plan_function_calling(
    model: ModelRecord,
    *,
    prompt: str,
    tools: tuple[ToolDefinition, ...],
    max_requests: int,
) -> CapabilityPlan:
    """Plan Function calling without Thinking or Structured Outputs."""
    track = CapabilityTrack.FUNCTION_CALLING
    if not _supported(model, track.value):
        return _plan((_unsupported(model, track, prompt),), max_requests=max_requests)
    cell = CapabilityCell(
        cell_id=f"{model.identifier}-function-calling",
        model=model.identifier,
        track=track,
        status=CapabilityCellStatus.PLANNED,
        prompt=prompt,
        tools=tools,
    )
    return _plan((cell,), max_requests=max_requests)


def load_vision_fixture(path: Path, *, workspace_root: Path) -> VisionFixture:
    """Load, constrain, and hash-check one reviewed protected PNG manifest."""
    try:
        payload = _YAML_MAPPING.validate_python(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
        fixture = VisionFixture.model_validate(payload)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as error:
        message = f"cannot load vision fixture {path}"
        raise ValueError(message) from error
    source_path = (workspace_root / fixture.source_path).resolve()
    protected_root = (workspace_root / "processed-data").resolve()
    if not source_path.is_relative_to(protected_root):
        message = "vision fixture must reference protected processed-data"
        raise ValueError(message)
    if (
        fixture.review_status != "reviewed"
        or fixture.media_type != "image/png"
        or source_path.suffix.casefold() != ".png"
    ):
        message = "vision fixture must be a reviewed PNG"
        raise ValueError(message)
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if digest != fixture.sha256:
        message = "vision fixture hash mismatch"
        raise ValueError(message)
    return fixture.model_copy(update={"source_path": source_path})


def plan_vision(
    model: ModelRecord,
    *,
    fixture: VisionFixture,
    max_requests: int,
) -> CapabilityPlan:
    """Plan one hash-pinned reviewed PNG request."""
    track = CapabilityTrack.VISION
    if not _supported(model, track.value):
        return _plan(
            (_unsupported(model, track, fixture.prompt),),
            max_requests=max_requests,
        )
    cell = CapabilityCell(
        cell_id=f"{model.identifier}-{fixture.case_id}",
        model=model.identifier,
        track=track,
        status=CapabilityCellStatus.PLANNED,
        prompt=fixture.prompt,
        vision_fixture=fixture,
    )
    return _plan((cell,), max_requests=max_requests)


def plan_context_limit(
    model: ModelRecord,
    *,
    prompt: str,
    estimated_input_tokens: int,
    context_limit: int,
    max_requests: int,
) -> CapabilityPlan:
    """Label known overflow unsupported without dispatching it."""
    status = (
        CapabilityCellStatus.UNSUPPORTED
        if estimated_input_tokens > context_limit
        else CapabilityCellStatus.PLANNED
    )
    reason = (
        "estimated input exceeds context limit"
        if status is CapabilityCellStatus.UNSUPPORTED
        else None
    )
    cell = CapabilityCell(
        cell_id=f"{model.identifier}-context-{estimated_input_tokens}",
        model=model.identifier,
        track=CapabilityTrack.CONTEXT_LIMIT,
        status=status,
        prompt=prompt,
        estimated_input_tokens=estimated_input_tokens,
        context_limit=context_limit,
        reason=reason,
    )
    return _plan((cell,), max_requests=max_requests)


async def execute_capability_plan(
    plan: CapabilityPlan,
    backend: CapabilityBackend,
) -> tuple[CapabilityResult, ...]:
    """Invoke planned cells once and retain unsupported or failed evidence."""
    unsupported_codes = {"40002", "40009", "40084"}
    results: list[CapabilityResult] = []
    for cell in plan.cells:
        if cell.status is CapabilityCellStatus.UNSUPPORTED:
            results.append(
                CapabilityResult(
                    cell_id=cell.cell_id,
                    model=cell.model,
                    track=cell.track,
                    status=CapabilityResultStatus.UNSUPPORTED,
                    error=cell.reason,
                )
            )
            continue
        try:
            outcome = await backend(cell)
        except ProviderApiError as error:
            status = (
                CapabilityResultStatus.UNSUPPORTED
                if error.provider_code in unsupported_codes
                else CapabilityResultStatus.FAILED
            )
            results.append(
                CapabilityResult(
                    cell_id=cell.cell_id,
                    model=cell.model,
                    track=cell.track,
                    status=status,
                    provider_code=error.provider_code,
                    error=redact_text(str(error)),
                )
            )
        except Exception as error:  # noqa: BLE001 - failures are retained evidence.
            results.append(
                CapabilityResult(
                    cell_id=cell.cell_id,
                    model=cell.model,
                    track=cell.track,
                    status=CapabilityResultStatus.FAILED,
                    error=redact_text(str(error)),
                )
            )
        else:
            results.append(
                CapabilityResult(
                    cell_id=cell.cell_id,
                    model=cell.model,
                    track=cell.track,
                    status=CapabilityResultStatus.SUPPORTED,
                    output=outcome.output,
                    latency_ms=outcome.latency_ms,
                )
            )
    return tuple(results)
