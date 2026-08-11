"""Monotonic stream timing plus bounded closed-loop and fixed-rate execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise
from typing import TYPE_CHECKING, ClassVar, Protocol, Self

import anyio
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import override

from hcx_eval.metrics.latency import (
    LatencyObservation,
    LatencySummary,
    percentile,
    summarize_latency,
)
from hcx_eval.metrics.statistics import ConfidenceInterval, bootstrap_mean_ci
from hcx_eval.schemas.results import ApiFamily  # noqa: TC001 - Pydantic runtime field.

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

    from hcx_eval.clients.sse import ParsedStream


class ArrivalMode(StrEnum):
    """Load-generation mode for one latency cell."""

    CLOSED_LOOP = "closed-loop"
    FIXED_RATE = "fixed-rate"


class LatencyPhase(StrEnum):
    """Warm-up or measured label retained on every attempt."""

    WARMUP = "warmup"
    MEASURED = "measured"


class LatencyCell(BaseModel):
    """One bounded model/load/input/output latency cell."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    model: str = Field(min_length=1)
    api_family: ApiFamily
    concurrency: int = Field(gt=0)
    stream: bool
    connection_reused: bool = True
    input_class: str = Field(min_length=1)
    target_output_tokens: int = Field(gt=0)
    warmup_successes: int = Field(ge=0)
    measured_attempts: int = Field(gt=0)
    arrival_mode: ArrivalMode
    fixed_rate_rps: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_arrival_rate(self) -> Self:
        """Require a rate only for fixed-rate scheduling."""
        if self.arrival_mode is ArrivalMode.FIXED_RATE:
            if self.fixed_rate_rps is None:
                message = "fixed-rate cells require fixed_rate_rps"
                raise ValueError(message)
        elif self.fixed_rate_rps is not None:
            message = "closed-loop cells cannot set fixed_rate_rps"
            raise ValueError(message)
        return self

    @property
    def attempt_count(self) -> int:
        """Return the explicit attempt count for preflight budgeting."""
        return self.warmup_successes + self.measured_attempts


class LatencyMeasurement(BaseModel):
    """One backend result before warm-up classification."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    success: bool
    status_code: int | None = Field(default=None, ge=100, le=599)
    e2e_ms: float | None = Field(default=None, ge=0)
    error_kind: str | None = None

    @model_validator(mode="after")
    def require_success_duration(self) -> Self:
        """Require a duration for successful measurements."""
        if self.success and self.e2e_ms is None:
            message = "successful measurement requires e2e_ms"
            raise ValueError(message)
        return self


class LatencyAttempt(LatencyMeasurement):
    """One retained result with stable sample index and phase."""

    sample_index: int = Field(ge=0)
    phase: LatencyPhase


class LatencyBackend(Protocol):
    """Injected request boundary for latency scheduling."""

    def __call__(
        self,
        cell: LatencyCell,
        sample_index: int,
    ) -> Awaitable[LatencyMeasurement]:
        """Measure one request."""
        ...


@dataclass(frozen=True, slots=True)
class LatencyPlanLimitError(ValueError):
    """Latency cells exceed their approved request ceiling."""

    planned: int
    ceiling: int

    @override
    def __str__(self) -> str:
        return f"planned {self.planned} requests exceeds ceiling {self.ceiling}"


class LatencyPlan(BaseModel):
    """Fully enumerated latency cells and exact maximum attempts."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    max_requests: int = Field(gt=0)
    cells: tuple[LatencyCell, ...]

    @property
    def request_count(self) -> int:
        """Return the exact scheduled attempt count."""
        return sum(cell.attempt_count for cell in self.cells)


class StreamTimingMetrics(BaseModel):
    """Derived measurements from one monotonic streaming request."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    response_headers_ms: float = Field(ge=0)
    ttft_ms: float | None = Field(default=None, ge=0)
    final_content_ms: float | None = Field(default=None, ge=0)
    close_ms: float = Field(ge=0)
    e2e_ms: float = Field(ge=0)
    tpot_ms: float | None = Field(default=None, ge=0)
    inter_token_gap_p95_ms: float | None = Field(default=None, ge=0)
    max_stall_ms: float | None = Field(default=None, ge=0)
    output_tokens_per_second: float | None = Field(default=None, ge=0)


class LatencyCellSummary(BaseModel):
    """Measured statistics with explicit warm-up and failure counts."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    total_attempts: int = Field(ge=0)
    warmup_attempts: int = Field(ge=0)
    measured_attempts: int = Field(ge=0)
    measured_successes: int = Field(ge=0)
    measured_failures: int = Field(ge=0)
    e2e: LatencySummary | None = None
    mean_ci: ConfidenceInterval | None = None


def plan_latency(
    cells: Sequence[LatencyCell],
    *,
    max_requests: int,
) -> LatencyPlan:
    """Validate the complete cell attempt count without truncation."""
    if max_requests <= 0:
        message = "latency request ceiling must be positive"
        raise ValueError(message)
    planned = sum(cell.attempt_count for cell in cells)
    if planned > max_requests:
        raise LatencyPlanLimitError(planned=planned, ceiling=max_requests)
    return LatencyPlan(max_requests=max_requests, cells=tuple(cells))


def derive_stream_timing(
    stream: ParsedStream,
    *,
    dispatched_at: float,
    output_tokens: int,
) -> StreamTimingMetrics:
    """Derive TTFT/E2E/TPOT solely from one monotonic client clock."""
    if stream.response_headers_at is None or stream.closed_at is None:
        message = "stream is missing headers or close timestamp"
        raise ValueError(message)
    content_times = tuple(event.received_at for event in stream.events if event.content)
    timeline = (stream.response_headers_at, *content_times, stream.closed_at)
    if any(value < dispatched_at for value in timeline) or any(
        later < earlier for earlier, later in pairwise(timeline)
    ):
        message = "stream timestamps are not monotonic"
        raise ValueError(message)
    first = content_times[0] if content_times else None
    final = content_times[-1] if content_times else None
    gaps_ms = tuple(
        (later - earlier) * 1000 for earlier, later in pairwise(content_times)
    )
    token_span = None if first is None or final is None else final - first
    tpot_ms = (
        None
        if token_span is None or output_tokens <= 1
        else (token_span * 1000) / (output_tokens - 1)
    )
    tokens_per_second = (
        None
        if token_span is None or token_span <= 0 or output_tokens <= 1
        else output_tokens / token_span
    )
    return StreamTimingMetrics(
        response_headers_ms=(stream.response_headers_at - dispatched_at) * 1000,
        ttft_ms=None if first is None else (first - dispatched_at) * 1000,
        final_content_ms=None if final is None else (final - dispatched_at) * 1000,
        close_ms=(stream.closed_at - dispatched_at) * 1000,
        e2e_ms=(stream.closed_at - dispatched_at) * 1000,
        tpot_ms=tpot_ms,
        inter_token_gap_p95_ms=(None if not gaps_ms else percentile(gaps_ms, 0.95)),
        max_stall_ms=None if not gaps_ms else max(gaps_ms),
        output_tokens_per_second=tokens_per_second,
    )


def _label_attempts(
    measurements: Sequence[LatencyMeasurement],
    *,
    warmup_successes: int,
) -> tuple[LatencyAttempt, ...]:
    warmup_completed = 0
    attempts: list[LatencyAttempt] = []
    for sample_index, measurement in enumerate(measurements):
        phase = (
            LatencyPhase.WARMUP
            if warmup_completed < warmup_successes
            else LatencyPhase.MEASURED
        )
        attempts.append(
            LatencyAttempt(
                success=measurement.success,
                status_code=measurement.status_code,
                e2e_ms=measurement.e2e_ms,
                error_kind=measurement.error_kind,
                sample_index=sample_index,
                phase=phase,
            )
        )
        if phase is LatencyPhase.WARMUP and measurement.success:
            warmup_completed += 1
    return tuple(attempts)


def summarize_latency_attempts(
    attempts: Sequence[LatencyAttempt],
    *,
    bootstrap_resamples: int = 2_000,
    seed: int = 0,
) -> LatencyCellSummary:
    """Exclude labeled warm-up from estimates while retaining every count."""
    measured = tuple(
        attempt for attempt in attempts if attempt.phase is LatencyPhase.MEASURED
    )
    observations = tuple(
        LatencyObservation(
            success=attempt.success,
            elapsed_ms=attempt.e2e_ms,
            status_code=attempt.status_code,
        )
        for attempt in measured
    )
    successful_values = tuple(
        attempt.e2e_ms
        for attempt in measured
        if attempt.success and attempt.e2e_ms is not None
    )
    e2e = None if not successful_values else summarize_latency(observations)
    mean_ci = (
        None
        if not successful_values
        else bootstrap_mean_ci(
            successful_values,
            resamples=bootstrap_resamples,
            seed=seed,
        )
    )
    successes = len(successful_values)
    return LatencyCellSummary(
        total_attempts=len(attempts),
        warmup_attempts=len(attempts) - len(measured),
        measured_attempts=len(measured),
        measured_successes=successes,
        measured_failures=len(measured) - successes,
        e2e=e2e,
        mean_ci=mean_ci,
    )


async def execute_latency_cell(
    cell: LatencyCell,
    backend: LatencyBackend,
    *,
    sleep: Callable[[float], Awaitable[None]] = anyio.sleep,
) -> tuple[LatencyAttempt, ...]:
    """Schedule every bounded attempt and retain backend exceptions as failures."""
    measurements: list[LatencyMeasurement | None] = [None] * cell.attempt_count
    limiter = anyio.CapacityLimiter(cell.concurrency)

    async def run_one(sample_index: int) -> None:
        async with limiter:
            try:
                measurement = await backend(cell, sample_index)
            except Exception as error:  # noqa: BLE001 - failed attempts are evidence.
                measurement = LatencyMeasurement(
                    success=False,
                    error_kind=type(error).__name__,
                )
            measurements[sample_index] = measurement

    async with anyio.create_task_group() as task_group:
        for sample_index in range(cell.attempt_count):
            _ = task_group.start_soon(run_one, sample_index)
            if (
                cell.arrival_mode is ArrivalMode.FIXED_RATE
                and sample_index + 1 < cell.attempt_count
            ):
                if cell.fixed_rate_rps is None:
                    raise AssertionError
                await sleep(1 / cell.fixed_rate_rps)
    complete = tuple(measurement for measurement in measurements if measurement)
    if len(complete) != cell.attempt_count:
        raise AssertionError
    return _label_attempts(complete, warmup_successes=cell.warmup_successes)
