from hcx_eval.runners.capabilities import (
    CapabilityTrack,
    ToolDefinition,
    plan_function_calling,
)
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus


def test_function_calling_has_its_own_tool_only_request() -> None:
    model = ModelRecord(
        identifier="HCX-005",
        status=ModelStatus.LIVE,
        api_families=("native-v3",),
        capabilities=(
            Capability(
                name="function_calling",
                supported=True,
                evidence=("probe:supported",),
            ),
        ),
        evidence=("fixture",),
    )
    tool = ToolDefinition(
        name="calculate_pension",
        parameters={"type": "object", "required": ["amount"]},
    )

    plan = plan_function_calling(
        model,
        prompt="calculate",
        tools=(tool,),
        max_requests=1,
    )

    assert plan.request_count == 1
    assert plan.cells[0].track is CapabilityTrack.FUNCTION_CALLING
    assert plan.cells[0].tools == (tool,)
    assert plan.cells[0].thinking_effort is None
    assert plan.cells[0].response_schema is None
