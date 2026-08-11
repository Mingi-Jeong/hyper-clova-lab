from __future__ import annotations

from typing import TYPE_CHECKING

from hcx_eval.runners.capabilities import CapabilityTrack, plan_structured_output
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus

if TYPE_CHECKING:
    from pydantic import JsonValue


def test_structured_output_is_planned_without_thinking() -> None:
    model = ModelRecord(
        identifier="HCX-007",
        status=ModelStatus.LIVE,
        api_families=("native-v3",),
        capabilities=(
            Capability(
                name="structured_outputs",
                supported=True,
                evidence=("probe:supported",),
            ),
        ),
        evidence=("fixture",),
    )
    schema: JsonValue = {"type": "object", "required": ["code"]}

    plan = plan_structured_output(
        model,
        prompt="return code",
        response_schema=schema,
        max_requests=1,
    )

    assert plan.request_count == 1
    assert plan.cells[0].track is CapabilityTrack.STRUCTURED_OUTPUTS
    assert plan.cells[0].thinking_effort is None
    assert plan.cells[0].response_schema == schema
