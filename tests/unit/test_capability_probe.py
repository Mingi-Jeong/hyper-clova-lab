import pytest

from hcx_eval.clients.base import ErrorKind, ProviderApiError
from hcx_eval.registry.capability_probe import (
    CapabilityProbePlan,
    ProbeCapability,
    ProbeStatus,
    execute_capability_probes,
)


@pytest.mark.anyio
async def test_probe_records_unsupported_without_combining_requests() -> None:
    # Given
    calls: list[tuple[str, ProbeCapability]] = []

    async def call(model: str, capability: ProbeCapability) -> None:
        calls.append((model, capability))
        if capability is ProbeCapability.THINKING:
            raise ProviderApiError(
                kind=ErrorKind.INVALID_REQUEST,
                endpoint="https://offline.invalid/v3/chat-completions/HCX-007",
                http_status=400,
                provider_code="40009",
            )

    plan = CapabilityProbePlan(
        model="HCX-007",
        probes=(ProbeCapability.THINKING, ProbeCapability.STRUCTURED_OUTPUTS),
    )

    # When
    results = await execute_capability_probes(plan, call)

    # Then
    assert calls == [
        ("HCX-007", ProbeCapability.THINKING),
        ("HCX-007", ProbeCapability.STRUCTURED_OUTPUTS),
    ]
    assert results[0].status is ProbeStatus.UNSUPPORTED
    assert results[0].provider_code == "40009"
    assert results[1].status is ProbeStatus.SUPPORTED
