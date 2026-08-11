"""Write-once orchestration for the two reports and Pareto chart projections."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from hcx_eval.reports.actual_results import render_actual_results
from hcx_eval.reports.charts import render_pareto_charts
from hcx_eval.reports.pension_insights import render_pension_insights

if TYPE_CHECKING:
    from pathlib import Path

    from hcx_eval.reports.models import ReportBundle

_PROTECTED_NAMES = frozenset(
    {
        ".hermes",
        "docs",
        "naver-clova-studio-instructions-all-docs",
        "processed-data",
    }
)


@dataclass(frozen=True, slots=True)
class ReportPaths:
    """Paths written for one immutable report bundle."""

    actual_results: Path
    pension_insights: Path
    charts: tuple[Path, ...]


def _write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def generate_reports(bundle: ReportBundle, *, results_root: Path) -> ReportPaths:
    """Generate separate evidence and insight reports without overwriting files."""
    resolved_root = results_root.resolve()
    if any(part in _PROTECTED_NAMES for part in resolved_root.parts):
        message = "report output cannot be beneath a protected source root"
        raise ValueError(message)
    report_root = resolved_root / "reports" / bundle.run_id
    chart_root = report_root / "charts"
    chart_payloads = render_pareto_charts(bundle.pareto_points)
    chart_paths = tuple(chart_root / name for name in sorted(chart_payloads))
    actual_path = report_root / "ACTUAL_TEST_RESULTS.md"
    insights_path = report_root / "FINANCIAL_PENSION_MODEL_INSIGHTS.md"
    targets = (actual_path, insights_path, *chart_paths)
    existing = next((path for path in targets if path.exists()), None)
    if existing is not None:
        raise FileExistsError(existing)
    chart_names = tuple(path.name for path in chart_paths)
    actual = render_actual_results(bundle, chart_names).encode()
    insights = render_pension_insights(bundle, chart_names).encode()
    _write_once(actual_path, actual)
    _write_once(insights_path, insights)
    for path in chart_paths:
        _write_once(path, chart_payloads[path.name])
    return ReportPaths(
        actual_results=actual_path,
        pension_insights=insights_path,
        charts=chart_paths,
    )
