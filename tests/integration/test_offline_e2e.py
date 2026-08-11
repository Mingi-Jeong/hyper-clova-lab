from __future__ import annotations

from typing import TYPE_CHECKING

import anyio
import httpx2

from hcx_eval.clients.base import RequestBudget, RequestPolicy
from hcx_eval.clients.openai_compat import OpenAICompatibleClient
from hcx_eval.registry.discovery import discover_models, write_model_registry
from hcx_eval.reports.models import (
    ArtifactReference,
    EvidenceClaim,
    ReportBundle,
    ReportTableId,
    not_run_table,
)
from hcx_eval.reports.writer import generate_reports
from hcx_eval.runners.generation import (
    AdapterGenerationBackend,
    execute_generation_plan,
)
from hcx_eval.runners.smoke import plan_smoke

if TYPE_CHECKING:
    from pathlib import Path


async def _run_mock_discovery_smoke_artifacts_and_reports_end_to_end(
    tmp_path: Path,
) -> None:
    requests: list[str] = []
    marker = "fixture-only-credential"

    async def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(f"{request.method} {request.url.path}")
        if request.url.path.endswith("/models"):
            return httpx2.Response(
                200,
                json={"data": [{"id": "HCX-MOCK", "object": "model"}]},
                request=request,
            )
        return httpx2.Response(
            200,
            json={
                "id": "mock-response",
                "model": "HCX-MOCK",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "연결 성공"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            },
            request=request,
        )

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key=marker,
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=2, max_tokens=8)),
        transport=httpx2.MockTransport(handler),
    )
    raw_models = tmp_path / "e2e" / "models.raw.json"
    discovery = await discover_models(
        client=client,
        documented=(),
        raw_output=raw_models,
    )
    registry_path = tmp_path / "e2e" / "model-registry.json"
    _ = write_model_registry(discovery.models, registry_path)
    plan = plan_smoke(
        discovery.models,
        run_id="offline-e2e",
        dataset_sha256="a" * 64,
        max_requests=1,
        max_tokens=4,
    )
    summary = await execute_generation_plan(
        plan,
        backend=AdapterGenerationBackend(openai=client),
        results_root=tmp_path / "runs",
        docs_snapshot_sha256="b" * 64,
    )

    reference = ArtifactReference(
        artifact_id="raw-smoke",
        path="runs/offline-e2e/raw/segment-000001.jsonl",
    )
    manifest = ArtifactReference(
        artifact_id="registry",
        path="e2e/model-registry.json",
    )
    bundle = ReportBundle(
        run_id="offline-e2e",
        manifest=manifest,
        scope=("MockTransport discovery and smoke",),
        exclusions=("live CLOVA API",),
        factual_claims=(
            EvidenceClaim(
                statement="One mock smoke request completed.",
                evidence=(reference,),
            ),
        ),
        tables=tuple(not_run_table(table_id, manifest) for table_id in ReportTableId),
        cost_basis="unknown",
        reproduction_commands=(
            "uv run pytest -q tests/integration/test_offline_e2e.py",
        ),
    )
    reports = generate_reports(bundle, results_root=tmp_path)

    assert requests == [
        "GET /v1/openai/models",
        "POST /v1/openai/chat/completions",
    ]
    assert discovery.external_requests == 1
    assert summary.executed == 1
    assert summary.failed == 0
    assert reports.actual_results.is_file()
    assert reports.pension_insights.is_file()
    async for path in anyio.Path(tmp_path).rglob("*"):
        if await path.is_file():
            assert marker.encode() not in await path.read_bytes()


def test_mock_e2e_runs_under_anyio_backend(tmp_path: Path) -> None:
    anyio.run(_run_mock_discovery_smoke_artifacts_and_reports_end_to_end, tmp_path)
