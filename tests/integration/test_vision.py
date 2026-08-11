from pathlib import Path

from hcx_eval.runners.capabilities import (
    CapabilityCellStatus,
    CapabilityTrack,
    load_vision_fixture,
    plan_context_limit,
    plan_vision,
)
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus


def _hcx005() -> ModelRecord:
    return ModelRecord(
        identifier="HCX-005",
        status=ModelStatus.LIVE,
        api_families=("native-v3",),
        capabilities=(
            Capability(
                name="vision",
                supported=True,
                evidence=("probe:supported",),
            ),
        ),
        evidence=("fixture",),
    )


def test_vision_requires_reviewed_hash_pinned_png_fixture() -> None:
    fixture = load_vision_fixture(
        Path("cases/fixtures/vision_hcx005.yaml"),
        workspace_root=Path.cwd(),
    )
    plan = plan_vision(_hcx005(), fixture=fixture, max_requests=1)

    assert plan.request_count == 1
    assert plan.cells[0].track is CapabilityTrack.VISION
    assert plan.cells[0].vision_fixture == fixture
    assert fixture.source_path.suffix == ".png"


def test_context_overflow_is_labeled_unsupported_without_dispatch() -> None:
    plan = plan_context_limit(
        _hcx005(),
        prompt="oversized",
        estimated_input_tokens=8_001,
        context_limit=8_000,
        max_requests=1,
    )

    assert plan.request_count == 0
    assert plan.cells[0].status is CapabilityCellStatus.UNSUPPORTED
    assert plan.cells[0].reason == "estimated input exceeds context limit"
