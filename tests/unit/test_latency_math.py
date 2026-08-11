from __future__ import annotations

import anyio
import pytest

from hcx_eval.runners.latency import (
    ArrivalMode,
    LatencyCell,
    LatencyMeasurement,
    LatencyPhase,
    LatencyPlanLimitError,
    execute_latency_cell,
    plan_latency,
    summarize_latency_attempts,
)
from hcx_eval.schemas.results import ApiFamily


def _cell(
    *,
    mode: ArrivalMode = ArrivalMode.CLOSED_LOOP,
    warmup: int = 1,
    measured: int = 2,
    concurrency: int = 2,
) -> LatencyCell:
    return LatencyCell(
        model="HCX-005",
        api_family=ApiFamily.OPENAI_COMPAT,
        concurrency=concurrency,
        stream=True,
        input_class="short",
        target_output_tokens=64,
        warmup_successes=warmup,
        measured_attempts=measured,
        arrival_mode=mode,
        fixed_rate_rps=2.0 if mode is ArrivalMode.FIXED_RATE else None,
    )


def test_latency_plan_refuses_an_implicit_cartesian_expansion() -> None:
    cells = (_cell(), _cell(concurrency=1))
    with pytest.raises(LatencyPlanLimitError, match="6 requests exceeds ceiling 5"):
        _ = plan_latency(cells, max_requests=5)

    plan = plan_latency(cells, max_requests=6)
    assert plan.request_count == 6


@pytest.mark.anyio
async def test_latency_runner_bounds_concurrency_and_labels_first_success_warmup() -> (
    None
):
    in_flight = 0
    max_in_flight = 0

    async def backend(cell: LatencyCell, sample_index: int) -> LatencyMeasurement:
        nonlocal in_flight, max_in_flight
        _ = cell
        in_flight += 1
        max_in_flight = max(max_in_flight, in_flight)
        await anyio.sleep(0.001)
        in_flight -= 1
        return LatencyMeasurement(
            success=sample_index != 0,
            status_code=500 if sample_index == 0 else 200,
            e2e_ms=float(sample_index + 1),
        )

    attempts = await execute_latency_cell(_cell(), backend)

    assert len(attempts) == 3
    assert max_in_flight <= 2
    assert tuple(attempt.phase for attempt in attempts) == (
        LatencyPhase.WARMUP,
        LatencyPhase.WARMUP,
        LatencyPhase.MEASURED,
    )
    assert not attempts[0].success
    summary = summarize_latency_attempts(attempts, bootstrap_resamples=100, seed=1)
    assert summary.total_attempts == 3
    assert summary.warmup_attempts == 2
    assert summary.measured_attempts == 1
    assert summary.measured_successes == 1
    assert summary.measured_failures == 0
    assert summary.e2e is not None
    assert summary.e2e.p50_ms == 3.0
    assert summary.mean_ci is not None


@pytest.mark.anyio
async def test_fixed_rate_schedules_arrivals_without_exceeding_concurrency() -> None:
    sleeps: list[float] = []

    async def backend(cell: LatencyCell, sample_index: int) -> LatencyMeasurement:
        _ = (cell, sample_index)
        return LatencyMeasurement(success=True, status_code=200, e2e_ms=1)

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    attempts = await execute_latency_cell(
        _cell(
            mode=ArrivalMode.FIXED_RATE,
            warmup=0,
            measured=3,
            concurrency=1,
        ),
        backend,
        sleep=fake_sleep,
    )

    assert len(attempts) == 3
    assert sleeps == [0.5, 0.5]
