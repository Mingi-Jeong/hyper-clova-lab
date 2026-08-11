"""Small deterministic Markdown primitives shared by both reports."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hcx_eval.reports.models import TABLE_DEFINITIONS, ReportTableId
from hcx_eval.security import redact_text

if TYPE_CHECKING:
    from collections.abc import Iterable

    from hcx_eval.reports.models import (
        ArtifactReference,
        EvidenceClaim,
        ReportBundle,
        ReportTable,
    )


def safe_text(value: str) -> str:
    """Redact credentials and escape Markdown table delimiters/newlines."""
    return redact_text(value).replace("|", "\\|").replace("\n", " ")


def render_reference(reference: ArtifactReference) -> str:
    """Render a results-root-relative artifact link from a report directory."""
    return f"[{safe_text(reference.artifact_id)}](../../{reference.path})"


def render_references(references: Iterable[ArtifactReference]) -> str:
    """Render an ordered list of evidence links."""
    return ", ".join(render_reference(reference) for reference in references)


def render_claims(claims: Iterable[EvidenceClaim], *, empty: str) -> str:
    """Render every claim adjacent to its source links."""
    rendered = tuple(
        f"- {safe_text(claim.statement)} Evidence: {render_references(claim.evidence)}"
        for claim in claims
    )
    return "\n".join(rendered) if rendered else empty


def render_items(items: Iterable[str]) -> str:
    """Render deterministic Markdown bullets with final redaction."""
    return "\n".join(f"- {safe_text(item)}" for item in items)


def render_table(table: ReportTable) -> str:
    """Render one normative table and its aggregate evidence links."""
    title, headers = TABLE_DEFINITIONS[table.table_id]
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    rows = tuple(
        "| " + " | ".join(safe_text(cell) for cell in row) + " |" for row in table.rows
    )
    evidence = f"Evidence: {render_references(table.evidence)}"
    return "\n".join(
        (f"### {table.table_id} {title}", "", header, separator, *rows, "", evidence)
    )


def table_for(bundle: ReportBundle, table_id: ReportTableId) -> ReportTable:
    """Return a table after bundle completeness validation."""
    return next(table for table in bundle.tables if table.table_id is table_id)
