"""Seeded non-parametric confidence intervals."""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass

from hcx_eval.metrics.latency import percentile


@dataclass(frozen=True, slots=True)
class ConfidenceInterval:
    """Point estimate and two-sided interval."""

    estimate: float
    lower: float
    upper: float
    confidence: float
    resamples: int
    seed: int


def bootstrap_mean_ci(
    values: tuple[float, ...],
    *,
    confidence: float = 0.95,
    resamples: int = 2_000,
    seed: int = 0,
) -> ConfidenceInterval:
    """Return a deterministic percentile bootstrap interval for the mean."""
    if not values:
        message = "bootstrap requires at least one value"
        raise ValueError(message)
    if not 0 < confidence < 1:
        message = "confidence must be between zero and one"
        raise ValueError(message)
    if resamples <= 0:
        message = "resamples must be positive"
        raise ValueError(message)
    generator = random.Random(seed)  # noqa: S311 - reproducible statistics, not crypto.
    sample_size = len(values)
    estimates = tuple(
        statistics.fmean(generator.choices(values, k=sample_size))
        for _ in range(resamples)
    )
    alpha = (1 - confidence) / 2
    return ConfidenceInterval(
        estimate=statistics.fmean(values),
        lower=percentile(estimates, alpha),
        upper=percentile(estimates, 1 - alpha),
        confidence=confidence,
        resamples=resamples,
        seed=seed,
    )
