"""Versioned evaluation case schema."""

from typing import ClassVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    field_serializer,
    field_validator,
)

from hcx_eval.security import FrozenDict, FrozenJson, freeze_json, freeze_mapping


class EvaluationCase(BaseModel):
    """Validated task input with immutable gold and source traceability."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        arbitrary_types_allowed=True, frozen=True, extra="forbid"
    )

    case_id: str = Field(min_length=1)
    task: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    expected: FrozenJson
    source_ids: tuple[str, ...] = Field(min_length=1)
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    metadata: FrozenDict = Field(default_factory=FrozenDict)

    @field_validator("expected", mode="before")
    @classmethod
    def freeze_expected(cls, value: JsonValue) -> FrozenJson:
        """Deep-freeze expected output at the schema boundary."""
        return freeze_json(value)

    @field_validator("metadata", mode="before")
    @classmethod
    def freeze_metadata(cls, value: JsonValue) -> FrozenDict:
        """Deep-freeze metadata at the schema boundary."""
        if not isinstance(value, dict):
            message = "case metadata must be a JSON object"
            raise TypeError(message)
        return freeze_mapping(value)

    @field_serializer("expected")
    def serialize_expected(self, value: FrozenJson) -> JsonValue:
        """Thaw expected output into detached JSON."""
        return value.to_json()

    @field_serializer("metadata")
    def serialize_metadata(self, value: FrozenDict) -> dict[str, JsonValue]:
        """Thaw metadata into a detached JSON object."""
        return value.to_json()
