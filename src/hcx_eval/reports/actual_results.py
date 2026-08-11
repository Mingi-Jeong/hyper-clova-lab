# ruff: noqa: E501
"""Factual results report renderer with no inferred missing values."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hcx_eval.reports.models import ReportTableId
from hcx_eval.reports.rendering import (
    render_claims,
    render_items,
    render_reference,
    render_table,
    safe_text,
    table_for,
)

if TYPE_CHECKING:
    from hcx_eval.reports.models import ReportBundle


def render_actual_results(bundle: ReportBundle, chart_names: tuple[str, ...]) -> str:
    """Render the required empirical report from a validated bundle."""
    chart_status = (
        "\n".join(f"- [{name}](charts/{name})" for name in chart_names)
        if chart_names
        else "NOT_RUN — no measured quality/latency/cost points were supplied."
    )
    tables = {
        table_id: render_table(table_for(bundle, table_id))
        for table_id in ReportTableId
    }
    return f"""# Actual Test Results — {safe_text(bundle.run_id)}

State legend: `NOT_RUN`, `UNSUPPORTED`, `UNAVAILABLE`, `RATE_LIMITED`, and `INSUFFICIENT_N` are evidence states, not zero scores.

## 1. Executive factual summary

{render_claims(bundle.factual_claims, empty="NOT_RUN — no aggregate factual claim was supplied.")}

## 2. Scope and exclusions

Scope:

{render_items(bundle.scope)}

Exclusions:

{render_items(bundle.exclusions)}

## 3. Environment and reproducibility manifest

Manifest: {render_reference(bundle.manifest)}

## 4. Model/API availability

{tables[ReportTableId.MODEL_AVAILABILITY]}

## 5. Dataset and case counts

See the manifest and table evidence. Missing counts remain `NOT_RUN`; they are never inferred.

## 6. Quality scorecards with confidence intervals

{tables[ReportTableId.GENERATION_SCORECARD]}

{tables[ReportTableId.TASK_QUALITY]}

{tables[ReportTableId.GROUNDING_CITATIONS]}

{tables[ReportTableId.STRUCTURED_TOOLS]}

## 7. Latency and load results

{tables[ReportTableId.LATENCY_OPERATIONS]}

{tables[ReportTableId.EMBEDDING_API_TOOLS]}

## 8. Safety hard-gate results

{tables[ReportTableId.SAFETY]}

## 9. Cost/token usage with source date

Cost basis: {safe_text(bundle.cost_basis)}. Unknown pricing is not estimated.

## 10. Per-model strengths and reproducible failure cases

Only evidence-linked facts in the tables above are reportable. Unlinked narrative is intentionally omitted.

## 11. Statistical comparisons and Pareto frontier

{chart_status}

## 12. Limitations and invalid/incomplete cells

Every incomplete cell uses an explicit state. No missing measurement is converted to a plausible number.

## 13. Raw artifact index and exact reproduction commands

Primary evidence: {render_reference(bundle.manifest)}

```text
{chr(10).join(safe_text(command) for command in bundle.reproduction_commands)}
```
"""
