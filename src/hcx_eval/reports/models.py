"""Validated normalized inputs for deterministic report rendering."""

from __future__ import annotations

from enum import StrEnum
from pathlib import PurePosixPath
from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from hcx_eval.security import redact_text


class ReportTableId(StrEnum):
    """Required result tables from the evaluation plan."""

    MODEL_AVAILABILITY = "9.1"
    GENERATION_SCORECARD = "9.2"
    TASK_QUALITY = "9.3"
    GROUNDING_CITATIONS = "9.4"
    STRUCTURED_TOOLS = "9.5"
    SAFETY = "9.6"
    LATENCY_OPERATIONS = "9.7"
    EMBEDDING_API_TOOLS = "9.8"
    PENSION_ROUTING = "9.9"


TABLE_DEFINITIONS: dict[ReportTableId, tuple[str, tuple[str, ...]]] = {
    ReportTableId.MODEL_AVAILABILITY: (
        "Model availability and capabilities",
        (
            "Model",
            "Discovery source",
            "Status",
            "API family",
            "Text",
            "Vision",
            "Thinking",
            "Structured Outputs",
            "Function calling",
            "Context/output limits",
            "Evidence",
        ),
    ),
    ReportTableId.GENERATION_SCORECARD: (
        "Overall generation-model scorecard",
        (
            "Model/config",
            "Accuracy 20",
            "RAG 15",
            "Reasoning 15",
            "Safety 20",
            "Instruction 10",
            "Korean 5",
            "Operations 15",
            "Total",
            "Gate",
            "Grade",
        ),
    ),
    ReportTableId.TASK_QUALITY: (
        "Dataset/task quality",
        (
            "Model/config",
            "Task",
            "N",
            "Accuracy/EM/F1",
            "Fact recall",
            "Contradiction",
            "Unsupported claim",
            "95% CI",
            "Key failure IDs",
        ),
    ),
    ReportTableId.GROUNDING_CITATIONS: (
        "Grounding and citations",
        (
            "Model/retrieval",
            "Recall@5",
            "MRR@10",
            "nDCG@10",
            "Citation precision",
            "Citation recall",
            "Faithfulness",
            "Unsupported claims",
            "Added latency p95",
        ),
    ),
    ReportTableId.STRUCTURED_TOOLS: (
        "Structured output and tools",
        (
            "Model/mode",
            "JSON parse",
            "Schema valid",
            "Required fields",
            "Tool name accuracy",
            "Argument F1",
            "Unneeded calls",
            "Tool-result faithfulness",
        ),
    ),
    ReportTableId.SAFETY: (
        "Safety",
        (
            "Model/config",
            "PII leak",
            "Guarantee claim",
            "Fabrication",
            "Injection success",
            "Unsafe advice",
            "Over-refusal",
            "Gate",
        ),
    ),
    ReportTableId.LATENCY_OPERATIONS: (
        "Latency and operations",
        (
            "Model/config/load",
            "N",
            "TTFT p50/p95/p99",
            "E2E p50/p95/p99",
            "TPOT p50/p95",
            "Gap p95/p99",
            "Max stall",
            "tok/s",
            "Timeout",
            "429",
            "5xx",
            "Cost/request",
            "Cost/correct",
        ),
    ),
    ReportTableId.EMBEDDING_API_TOOLS: (
        "Embedding and API-tool scorecard",
        (
            "Model/API",
            "Task",
            "Quality metric",
            "Latency p50/p95/p99",
            "Throughput",
            "Error rate",
            "Incremental E2E latency",
            "Strengths",
            "Limitations",
        ),
    ),
    ReportTableId.PENSION_ROUTING: (
        "Pension-service routing recommendation",
        (
            "Pension use case",
            "Recommended model/API",
            "Fallback",
            "Required RAG",
            "Required Guard",
            "Target SLO",
            "Evidence",
            "Prohibited/unsafe use",
        ),
    ),
}


class ArtifactReference(BaseModel):
    """Safe relative link to immutable run evidence."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    artifact_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    path: str = Field(min_length=1)

    @field_validator("path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        """Reject paths that could escape the configured results root."""
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts or "\\" in value:
            message = "artifact path must be a safe POSIX-relative path"
            raise ValueError(message)
        return redact_text(value)


class EvidenceClaim(BaseModel):
    """A claim that cannot be rendered without one or more artifact links."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    statement: str = Field(min_length=1)
    evidence: tuple[ArtifactReference, ...] = Field(min_length=1)

    @field_validator("statement")
    @classmethod
    def redact_statement(cls, value: str) -> str:
        """Mask accidental credential material before report persistence."""
        return redact_text(value)


class ReportTable(BaseModel):
    """One normalized required table with table-level source evidence."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    table_id: ReportTableId
    rows: tuple[tuple[str, ...], ...] = Field(min_length=1)
    evidence: tuple[ArtifactReference, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_width(self) -> Self:
        """Require every row to match the normative table definition."""
        width = len(TABLE_DEFINITIONS[self.table_id][1])
        if any(len(row) != width for row in self.rows):
            message = f"table {self.table_id} rows must contain {width} cells"
            raise ValueError(message)
        return self


class ParetoPoint(BaseModel):
    """Measured quality, client latency, and priced cost for one model/config."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        extra="forbid",
        allow_inf_nan=False,
    )

    label: str = Field(min_length=1)
    quality: float = Field(ge=0, le=100)
    latency_ms: float = Field(gt=0)
    cost_per_request: float = Field(ge=0)
    evidence: tuple[ArtifactReference, ...] = Field(min_length=1)


class ReportBundle(BaseModel):
    """Complete normalized data required to write both final reports."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    run_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    manifest: ArtifactReference
    scope: tuple[str, ...] = Field(min_length=1)
    exclusions: tuple[str, ...] = Field(min_length=1)
    factual_claims: tuple[EvidenceClaim, ...] = ()
    insight_claims: tuple[EvidenceClaim, ...] = ()
    tables: tuple[ReportTable, ...]
    pareto_points: tuple[ParetoPoint, ...] = ()
    cost_basis: str = Field(min_length=1)
    reproduction_commands: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_complete_tables_and_points(self) -> Self:
        """Require each Section 9 table once and uniquely labeled chart points."""
        identifiers = tuple(table.table_id for table in self.tables)
        if len(identifiers) != len(ReportTableId) or set(identifiers) != set(
            ReportTableId
        ):
            message = "report bundle must contain every Section 9 table exactly once"
            raise ValueError(message)
        labels = tuple(point.label for point in self.pareto_points)
        if len(labels) != len(set(labels)):
            message = "Pareto point labels must be unique"
            raise ValueError(message)
        return self


def not_run_table(
    table_id: ReportTableId,
    evidence: ArtifactReference,
) -> ReportTable:
    """Build an explicit missing-state row rather than inventing measurements."""
    width = len(TABLE_DEFINITIONS[table_id][1])
    return ReportTable(
        table_id=table_id,
        rows=(("NOT_RUN",) * width,),
        evidence=(evidence,),
    )
