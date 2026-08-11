from pathlib import Path

import pytest
from pydantic import ValidationError

from hcx_eval.reports.models import (
    ArtifactReference,
    EvidenceClaim,
    ParetoPoint,
    ReportBundle,
    ReportTable,
    ReportTableId,
    not_run_table,
)
from hcx_eval.reports.writer import generate_reports

_GOLDEN_ROOT = Path("tests/unit/reports/golden")


def _reference() -> ArtifactReference:
    return ArtifactReference(
        artifact_id="manifest",
        path="offline-fixture/manifest.json",
    )


def _bundle(*, with_points: bool = False) -> ReportBundle:
    reference = _reference()
    tables = [not_run_table(table_id, reference) for table_id in ReportTableId]
    availability = ReportTable(
        table_id=ReportTableId.MODEL_AVAILABILITY,
        rows=(
            (
                "HCX-FIXTURE",
                "mock registry",
                "UNAVAILABLE",
                "openai-compatible",
                "NOT_RUN",
                "UNSUPPORTED",
                "NOT_RUN",
                "NOT_RUN",
                "NOT_RUN",
                "unknown",
                "manifest",
            ),
        ),
        evidence=(reference,),
    )
    tables[0] = availability
    points = (
        (
            ParetoPoint(
                label="fixture-a",
                quality=80,
                latency_ms=250,
                cost_per_request=0.01,
                evidence=(reference,),
            ),
            ParetoPoint(
                label="fixture-b",
                quality=75,
                latency_ms=180,
                cost_per_request=0.005,
                evidence=(reference,),
            ),
        )
        if with_points
        else ()
    )
    return ReportBundle(
        run_id="offline-fixture",
        manifest=reference,
        scope=("offline mock validation",),
        exclusions=("live CLOVA API",),
        factual_claims=(
            EvidenceClaim(
                statement="No live provider request was made.",
                evidence=(reference,),
            ),
        ),
        insight_claims=(
            EvidenceClaim(
                statement="Model routing remains undecided until a live run.",
                evidence=(reference,),
            ),
        ),
        tables=tuple(tables),
        pareto_points=points,
        cost_basis="unknown",
        reproduction_commands=("uv run hcx-eval report --run-id offline-fixture",),
    )


def test_reports_match_golden_markdown_and_render_explicit_states(
    tmp_path: Path,
) -> None:
    paths = generate_reports(_bundle(), results_root=tmp_path)

    actual = paths.actual_results.read_text(encoding="utf-8")
    insights = paths.pension_insights.read_text(encoding="utf-8")
    assert actual == (_GOLDEN_ROOT / "ACTUAL_TEST_RESULTS.md").read_text(
        encoding="utf-8"
    )
    assert insights == (_GOLDEN_ROOT / "FINANCIAL_PENSION_MODEL_INSIGHTS.md").read_text(
        encoding="utf-8"
    )
    assert "NOT_RUN" in actual
    assert "UNSUPPORTED" in actual
    assert "UNAVAILABLE" in actual
    assert "[manifest](../../offline-fixture/manifest.json)" in actual
    assert paths.charts == ()


def test_pareto_charts_are_generated_and_reports_are_write_once(
    tmp_path: Path,
) -> None:
    bundle = _bundle(with_points=True)
    paths = generate_reports(bundle, results_root=tmp_path)

    assert {path.name for path in paths.charts} == {
        "quality-cost-pareto.svg",
        "quality-latency-pareto.svg",
    }
    assert all(path.stat().st_size > 0 for path in paths.charts)
    with pytest.raises(FileExistsError):
        _ = generate_reports(bundle, results_root=tmp_path)


def test_report_table_requires_evidence_links() -> None:
    with pytest.raises(ValidationError):
        _ = ReportTable(
            table_id=ReportTableId.SAFETY,
            rows=(("NOT_RUN",) * 8,),
            evidence=(),
        )
