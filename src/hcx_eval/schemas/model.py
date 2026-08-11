"""Model discovery and capability evidence schemas."""

from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class ModelStatus(StrEnum):
    """Evidence-backed model availability state."""

    LIVE = "live"
    RESTRICTED = "restricted"
    DEPRECATED = "deprecated"
    UNAVAILABLE = "unavailable"
    HISTORICAL_EXAMPLE_ONLY = "historical-example-only"
    DOCUMENTED = "documented"


class Capability(BaseModel):
    """One supported, unsupported, or unknown model capability."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    supported: bool | None = None
    evidence: tuple[str, ...] = ()


class ModelRecord(BaseModel):
    """Traceable model record merged from documentary and live sources."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    identifier: str = Field(min_length=1)
    status: ModelStatus
    api_families: tuple[str, ...] = ()
    endpoints: tuple[str, ...] = ()
    capabilities: tuple[Capability, ...] = ()
    evidence: tuple[str, ...] = Field(min_length=1)
