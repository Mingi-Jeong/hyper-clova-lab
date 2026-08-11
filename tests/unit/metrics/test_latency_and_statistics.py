import pytest

from hcx_eval.metrics.latency import LatencyObservation, summarize_latency
from hcx_eval.metrics.statistics import bootstrap_mean_ci


def test_latency_summary_retains_failures_and_uses_linear_percentiles() -> None:
    summary = summarize_latency(
        (
            LatencyObservation(success=True, elapsed_ms=10),
            LatencyObservation(success=True, elapsed_ms=20),
            LatencyObservation(success=True, elapsed_ms=30),
            LatencyObservation(success=True, elapsed_ms=40),
            LatencyObservation(success=False, elapsed_ms=None, status_code=429),
        )
    )

    assert summary.attempts == 5
    assert summary.successes == 4
    assert summary.failures == 1
    assert summary.rate_limit_count == 1
    assert summary.p50_ms == 25.0
    assert summary.p95_ms == pytest.approx(38.5)
    assert summary.p99_ms == pytest.approx(39.7)


def test_bootstrap_mean_ci_is_seeded_and_contains_point_estimate() -> None:
    first = bootstrap_mean_ci((1.0, 2.0, 3.0, 4.0), resamples=2_000, seed=7)
    second = bootstrap_mean_ci((1.0, 2.0, 3.0, 4.0), resamples=2_000, seed=7)

    assert first == second
    assert first.estimate == 2.5
    assert first.lower <= first.estimate <= first.upper


def test_latency_and_bootstrap_reject_empty_success_samples() -> None:
    with pytest.raises(ValueError, match="successful latency"):
        _ = summarize_latency((LatencyObservation(success=False, status_code=500),))
    with pytest.raises(ValueError, match="at least one value"):
        _ = bootstrap_mean_ci(())
