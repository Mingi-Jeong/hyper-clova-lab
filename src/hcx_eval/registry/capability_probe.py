"""Capability probe planning that avoids unsupported combinations."""

from enum import StrEnum
from typing import ClassVar, Protocol

from pydantic import BaseModel, ConfigDict

from hcx_eval.clients.base import ProviderApiError
from hcx_eval.schemas.model import ModelRecord, ModelStatus


class ProbeCapability(StrEnum):
    """Independently testable provider capability."""

    TEXT = "generation"
    STREAMING = "streaming"
    EMBEDDING = "embedding"
    THINKING = "thinking"
    VISION = "vision"
    STRUCTURED_OUTPUTS = "structured_outputs"
    FUNCTION_CALLING = "function_calling"


class CapabilityProbePlan(BaseModel):
    """A bounded list of independent probes for one model."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    model: str
    probes: tuple[ProbeCapability, ...]
    skipped_reason: str | None = None


class ProbeStatus(StrEnum):
    """Observed outcome of one isolated probe."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


class CapabilityProbeResult(BaseModel):
    """Provider-evidenced outcome of one capability request."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    model: str
    capability: ProbeCapability
    status: ProbeStatus
    provider_code: str | None = None


class ProbeCall(Protocol):
    """Wire-injectable single-capability request."""

    async def __call__(self, model: str, capability: ProbeCapability) -> None:
        """Dispatch one feature in isolation."""
        ...


def plan_capability_probes(record: ModelRecord) -> CapabilityProbePlan:
    """Plan only evidenced probes and never combine special v3 modes."""
    if record.status is not ModelStatus.LIVE:
        return CapabilityProbePlan(
            model=record.identifier,
            probes=(),
            skipped_reason=f"model status is {record.status}",
        )
    names = {capability.name for capability in record.capabilities}
    probes = tuple(
        candidate for candidate in ProbeCapability if candidate.value in names
    )
    return CapabilityProbePlan(model=record.identifier, probes=probes)


async def execute_capability_probes(
    plan: CapabilityProbePlan, call: ProbeCall
) -> tuple[CapabilityProbeResult, ...]:
    """Execute isolated probes and retain unsupported provider codes."""
    results: list[CapabilityProbeResult] = []
    for capability in plan.probes:
        try:
            await call(plan.model, capability)
        except ProviderApiError as error:
            unsupported = error.provider_code in {"40002", "40009", "40084"}
            status = ProbeStatus.UNSUPPORTED if unsupported else ProbeStatus.FAILED
            results.append(
                CapabilityProbeResult(
                    model=plan.model,
                    capability=capability,
                    status=status,
                    provider_code=error.provider_code,
                )
            )
        else:
            results.append(
                CapabilityProbeResult(
                    model=plan.model,
                    capability=capability,
                    status=ProbeStatus.SUPPORTED,
                )
            )
    return tuple(results)
