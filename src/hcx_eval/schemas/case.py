"""Versioned evaluation case schema."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class EvaluationCase(BaseModel):
    """Validated task input with immutable gold and source traceability."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    case_id: str = Field(min_length=1)
    task: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    expected: JsonValue
    source_ids: tuple[str, ...] = Field(min_length=1)
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    metadata: dict[str, JsonValue] = Field(default_factory=dict)
