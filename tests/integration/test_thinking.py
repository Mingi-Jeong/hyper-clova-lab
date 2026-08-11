import pytest
from pydantic import ValidationError

from hcx_eval.runners.capabilities import (
    CapabilityOutcome,
    CapabilityResultStatus,
    CapabilityTrack,
    ThinkingEffort,
    execute_capability_plan,
    plan_thinking,
)
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus


def _hcx007() -> ModelRecord:
    return ModelRecord(
        identifier="HCX-007",
        status=ModelStatus.LIVE,
        api_families=("native-v3",),
        capabilities=(
            Capability(
                name="thinking",
                supported=True,
                evidence=("probe:supported",),
            ),
        ),
        evidence=("fixture",),
    )


def test_thinking_levels_are_four_isolated_requests() -> None:
    plan = plan_thinking(_hcx007(), prompt="reason", max_requests=4)

    assert plan.request_count == 4
    assert tuple(cell.thinking_effort for cell in plan.cells) == tuple(ThinkingEffort)
    assert {cell.track for cell in plan.cells} == {CapabilityTrack.THINKING}
    assert all(cell.response_schema is None for cell in plan.cells)
    assert all(not cell.tools for cell in plan.cells)


def test_thinking_cannot_be_combined_with_structured_output() -> None:
    cell = plan_thinking(_hcx007(), prompt="reason", max_requests=4).cells[0]
    payload = cell.model_dump(mode="json")
    payload["response_schema"] = {"type": "object"}
    with pytest.raises(ValidationError, match="cannot be combined"):
        _ = type(cell).model_validate(payload)


@pytest.mark.anyio
async def test_capability_executor_dispatches_each_thinking_level_once() -> None:
    calls: list[ThinkingEffort | None] = []

    async def backend(cell: object) -> CapabilityOutcome:
        effort = getattr(cell, "thinking_effort", None)
        calls.append(effort)
        return CapabilityOutcome(output={"ok": True}, latency_ms=1)

    results = await execute_capability_plan(
        plan_thinking(_hcx007(), prompt="reason", max_requests=4),
        backend,
    )

    assert calls == list(ThinkingEffort)
    assert all(result.status is CapabilityResultStatus.SUPPORTED for result in results)
