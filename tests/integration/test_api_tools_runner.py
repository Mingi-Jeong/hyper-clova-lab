from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from hcx_eval.runners.api_tools import (
    ApiToolCase,
    ApiToolName,
    ApiToolOutcome,
    evaluate_api_tools,
)

if TYPE_CHECKING:
    from pydantic import JsonValue


class FixtureToolBackend:
    def __init__(self) -> None:
        self.calls: list[tuple[ApiToolName, str]] = []

    async def invoke(
        self,
        tool: ApiToolName,
        case: ApiToolCase,
    ) -> ApiToolOutcome:
        self.calls.append((tool, case.case_id))
        return ApiToolOutcome(output={"answer": "correct"}, latency_ms=12.5)


@pytest.mark.anyio
async def test_api_tools_keep_quality_gain_and_added_latency_separate() -> None:
    cases = (
        ApiToolCase(
            case_id="TOOL-1",
            payload={"query": "question"},
            expected={"answer": "correct"},
            baseline_quality=0.4,
            baseline_latency_ms=20,
        ),
    )
    backend = FixtureToolBackend()

    def scorer(actual: JsonValue, expected: JsonValue) -> float:
        return float(actual == expected)

    results = await evaluate_api_tools(
        cases,
        (ApiToolName.RERANKER, ApiToolName.ROUTER),
        backend=backend,
        scorer=scorer,
        max_requests=2,
    )

    assert len(results) == 2
    assert backend.calls == [
        (ApiToolName.RERANKER, "TOOL-1"),
        (ApiToolName.ROUTER, "TOOL-1"),
    ]
    assert all(result.tool_quality == 1.0 for result in results)
    assert all(result.quality_gain == 0.6 for result in results)
    assert all(result.added_latency_ms == 12.5 for result in results)
    assert all(result.end_to_end_latency_ms == 32.5 for result in results)


@pytest.mark.anyio
async def test_api_tool_runner_enforces_request_ceiling_before_dispatch() -> None:
    case = ApiToolCase(
        case_id="TOOL-1",
        payload={"query": "question"},
        expected={"answer": "correct"},
        baseline_quality=0,
        baseline_latency_ms=0,
    )
    backend = FixtureToolBackend()

    with pytest.raises(ValueError, match="2 requests exceeds ceiling 1"):
        _ = await evaluate_api_tools(
            (case,),
            (ApiToolName.RERANKER, ApiToolName.ROUTER),
            backend=backend,
            scorer=lambda actual, expected: float(actual == expected),
            max_requests=1,
        )
    assert backend.calls == []
