"""Failure-preserving latency summaries with linear percentiles."""

from __future__ import annotations

import math
from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_RATE_LIMIT = 429
_TIMEOUT = 408
_SERVER_ERROR = 500


class LatencyObservation(BaseModel):
    """One successful duration or retained failed attempt."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    success: bool
    elapsed_ms: float | None = Field(default=None, ge=0)
    status_code: int | None = Field(default=None, ge=100, le=599)

    @model_validator(mode="after")
    def require_success_duration(self) -> Self:
        """Require a measured duration for a successful attempt."""
        if self.success and self.elapsed_ms is None:
            message = "successful latency requires elapsed_ms"
            raise ValueError(message)
        return self


class LatencySummary(BaseModel):
    """Percentiles plus explicit failure counts."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    attempts: int = Field(ge=1)
    successes: int = Field(ge=1)
    failures: int = Field(ge=0)
    timeout_count: int = Field(ge=0)
    rate_limit_count: int = Field(ge=0)
    server_error_count: int = Field(ge=0)
    p50_ms: float = Field(ge=0)
    p95_ms: float = Field(ge=0)
    p99_ms: float = Field(ge=0)


def percentile(values: tuple[float, ...], quantile: float) -> float:
    """Return a deterministic linearly interpolated percentile."""
    if not values:
        message = "percentile requires at least one value"
        raise ValueError(message)
    if not 0 <= quantile <= 1:
        message = "quantile must be between zero and one"
        raise ValueError(message)
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + ((ordered[upper] - ordered[lower]) * fraction)


def summarize_latency(
    observations: tuple[LatencyObservation, ...],
) -> LatencySummary:
    """Summarize successes while retaining every failed attempt by class."""
    successful = tuple(
        observation.elapsed_ms
        for observation in observations
        if observation.success and observation.elapsed_ms is not None
    )
    if not successful:
        message = "at least one successful latency is required"
        raise ValueError(message)
    successes = len(successful)
    return LatencySummary(
        attempts=len(observations),
        successes=successes,
        failures=len(observations) - successes,
        timeout_count=sum(
            not item.success and item.status_code in {None, _TIMEOUT}
            for item in observations
        ),
        rate_limit_count=sum(
            not item.success and item.status_code == _RATE_LIMIT
            for item in observations
        ),
        server_error_count=sum(
            not item.success
            and item.status_code is not None
            and item.status_code >= _SERVER_ERROR
            for item in observations
        ),
        p50_ms=percentile(successful, 0.50),
        p95_ms=percentile(successful, 0.95),
        p99_ms=percentile(successful, 0.99),
    )
