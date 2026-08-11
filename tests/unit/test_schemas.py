from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from hcx_eval.schemas.results import (
    ApiFamily,
    ErrorDetail,
    RawResult,
    RequestSnapshot,
    Timing,
    Usage,
)


def test_raw_result_is_immutable_and_reconciles_usage() -> None:
    # Given: a valid failed request record.
    record = RawResult(
        run_id="run-1",
        request_id="request-1",
        case_id="case-1",
        model="HCX-005",
        api_family=ApiFamily.NATIVE_V3,
        prompt_version="v1",
        dataset_sha256="a" * 64,
        docs_snapshot_sha256="b" * 64,
        request=RequestSnapshot(payload={"messages": []}),
        timing=Timing(started_at=datetime.now(UTC), e2e_ms=1.5),
        usage=Usage(prompt_tokens=2, completion_tokens=3, total_tokens=5),
        error=ErrorDetail(kind="timeout", message="deadline"),
    )

    # When / Then: mutation is forbidden.
    with pytest.raises(ValidationError):
        record.model = "changed"


def test_usage_rejects_inconsistent_total() -> None:
    # Given / When / Then: token totals cannot contradict their components.
    with pytest.raises(ValidationError):
        _ = Usage(
            prompt_tokens=2,
            completion_tokens=3,
            thinking_tokens=1,
            total_tokens=5,
        )


def test_timing_rejects_ttft_after_end_to_end() -> None:
    # Given / When / Then: timing chronology is enforced at the boundary.
    with pytest.raises(ValidationError):
        _ = Timing(started_at=datetime.now(UTC), ttft_ms=10, e2e_ms=5)
