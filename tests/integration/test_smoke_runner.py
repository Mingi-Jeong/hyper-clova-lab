from __future__ import annotations

from typing import TYPE_CHECKING

import httpx2
import pytest

from hcx_eval.clients.base import RequestBudget, RequestPolicy
from hcx_eval.clients.openai_compat import OpenAICompatibleClient
from hcx_eval.runners.generation import (
    AdapterGenerationBackend,
    RequestPlanLimitError,
    execute_generation_plan,
)
from hcx_eval.runners.smoke import plan_smoke
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus

if TYPE_CHECKING:
    from pathlib import Path


def _model(
    identifier: str,
    *,
    status: ModelStatus,
    capability: str,
    api_family: str = "openai-compatible",
) -> ModelRecord:
    return ModelRecord(
        identifier=identifier,
        status=status,
        api_families=(api_family,),
        capabilities=(Capability(name=capability, supported=True),),
        evidence=("fixture",),
    )


def test_smoke_plan_includes_each_live_generation_model_once() -> None:
    registry = (
        _model("HCX-005", status=ModelStatus.LIVE, capability="generation"),
        _model(
            "HCX-007",
            status=ModelStatus.LIVE,
            capability="thinking",
            api_family="native-v3",
        ),
        _model("bge-m3", status=ModelStatus.LIVE, capability="embedding"),
        _model("HCX-003", status=ModelStatus.DOCUMENTED, capability="generation"),
    )

    plan = plan_smoke(
        registry,
        run_id="smoke-1",
        dataset_sha256="a" * 64,
        max_requests=2,
        max_tokens=8,
    )

    assert plan.request_count == 2
    assert tuple(job.model for job in plan.jobs) == ("HCX-005", "HCX-007")
    assert tuple(job.api_family.value for job in plan.jobs) == (
        "openai-compatible",
        "native-v3",
    )


def test_smoke_plan_refuses_to_truncate_at_request_ceiling() -> None:
    registry = (
        _model("HCX-005", status=ModelStatus.LIVE, capability="generation"),
        _model("HCX-007", status=ModelStatus.LIVE, capability="generation"),
    )

    with pytest.raises(RequestPlanLimitError, match="2 requests exceeds ceiling 1"):
        _ = plan_smoke(
            registry,
            run_id="smoke-1",
            dataset_sha256="a" * 64,
            max_requests=1,
            max_tokens=8,
        )


@pytest.mark.anyio
async def test_smoke_runner_uses_real_adapter_with_mock_transport(
    tmp_path: Path,
) -> None:
    # Given: one live model and a real compatible adapter on an offline wire.
    seen: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(
            200,
            json={
                "id": "chat-1",
                "model": "HCX-005",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "정상"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 2,
                    "completion_tokens": 1,
                    "total_tokens": 3,
                },
            },
            request=request,
        )

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="synthetic-key",
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=1, max_tokens=8)),
        transport=httpx2.MockTransport(handler),
    )
    registry = (_model("HCX-005", status=ModelStatus.LIVE, capability="generation"),)
    plan = plan_smoke(
        registry,
        run_id="smoke-mock",
        dataset_sha256="a" * 64,
        max_requests=1,
        max_tokens=8,
    )

    # When: the normal runner executes against the mock adapter.
    summary = await execute_generation_plan(
        plan,
        backend=AdapterGenerationBackend(openai=client),
        results_root=tmp_path,
        docs_snapshot_sha256="b" * 64,
    )

    # Then: exactly one bounded request and one append-only result exist.
    assert summary.executed == 1
    assert summary.failed == 0
    assert len(seen) == 1
    assert seen[0].url.host == "offline.invalid"
    raw = tmp_path / "smoke-mock" / "raw" / "segment-000001.jsonl"
    assert '"response_text":"정상"' in raw.read_text()
