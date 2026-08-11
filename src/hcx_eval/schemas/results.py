"""Raw request, result, error, timing, and usage schemas."""

from datetime import datetime
from enum import StrEnum
from typing import ClassVar, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    field_serializer,
    field_validator,
    model_validator,
)

from hcx_eval.security import (
    FrozenDict,
    FrozenJson,
    freeze_json,
    freeze_mapping,
    redact,
    redact_text,
)


class ApiFamily(StrEnum):
    """Provider protocol family used by a request."""

    NATIVE_V1 = "native-v1"
    NATIVE_V3 = "native-v3"
    OPENAI_COMPAT = "openai-compatible"
    API_TOOL = "api-tool"


class RequestSnapshot(BaseModel):
    """Persistable request content after recursive secret redaction."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        arbitrary_types_allowed=True, frozen=True, extra="forbid"
    )

    payload: FrozenDict
    headers: FrozenDict = Field(default_factory=FrozenDict)

    @field_validator("payload", "headers", mode="before")
    @classmethod
    def redact_secrets(cls, value: JsonValue) -> FrozenDict:
        """Redact request secrets before model construction."""
        redacted = redact(value)
        if not isinstance(redacted, dict):
            message = "request payload and headers must be JSON objects"
            raise TypeError(message)
        return freeze_mapping(redacted)

    @field_serializer("payload", "headers")
    def serialize_mapping(self, value: FrozenDict) -> dict[str, JsonValue]:
        """Thaw immutable request mappings into detached JSON objects."""
        return value.to_json()


class ErrorDetail(BaseModel):
    """Structured provider, transport, or validation failure."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    kind: str = Field(min_length=1)
    message: str = Field(min_length=1)
    retryable: bool = False
    provider_code: str | None = None

    @field_validator("message", mode="before")
    @classmethod
    def redact_message(cls, value: str) -> str:
        """Mask credential substrings in persisted error text."""
        return redact_text(value)


class Timing(BaseModel):
    """Client-clock request timing measurements in milliseconds."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    started_at: datetime
    response_headers_ms: float | None = Field(default=None, ge=0)
    ttft_ms: float | None = Field(default=None, ge=0)
    e2e_ms: float = Field(ge=0)
    tpot_ms: float | None = Field(default=None, ge=0)
    inter_token_gap_p95_ms: float | None = Field(default=None, ge=0)
    max_stall_ms: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_chronology(self) -> Self:
        """Ensure intermediate client-clock events precede completion."""
        if (
            self.response_headers_ms is not None
            and self.response_headers_ms > self.e2e_ms
        ):
            message = "response headers cannot arrive after request completion"
            raise ValueError(message)
        if self.ttft_ms is not None and self.ttft_ms > self.e2e_ms:
            message = "first token cannot arrive after request completion"
            raise ValueError(message)
        return self


class Usage(BaseModel):
    """Provider token accounting."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    thinking_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_total(self) -> Self:
        """Reconcile the provider total with all reported components."""
        components = self.prompt_tokens + self.completion_tokens + self.thinking_tokens
        if self.total_tokens != components:
            message = "total tokens must equal all token components"
            raise ValueError(message)
        return self


class RawResult(BaseModel):
    """Immutable raw outcome for every attempted provider request."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    run_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    model: str = Field(min_length=1)
    model_mode: str | None = None
    api_family: ApiFamily
    prompt_version: str = Field(min_length=1)
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    docs_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    request: RequestSnapshot
    response_raw: FrozenJson = Field(default_factory=lambda: freeze_json(None))
    response_text: str | None = None
    timing: Timing
    usage: Usage | None = None
    stream: bool = False
    connection_reused: bool = False
    concurrency: int = Field(default=1, gt=0)
    http_status: int | None = Field(default=None, ge=100, le=599)
    provider_status_code: str | None = None
    retry_count: int = Field(default=0, ge=0)
    error: ErrorDetail | None = None

    @field_validator("response_raw", mode="before")
    @classmethod
    def redact_response(cls, value: JsonValue) -> FrozenJson:
        """Redact response secrets before model construction."""
        return freeze_json(redact(value))

    @field_validator("response_text", mode="before")
    @classmethod
    def redact_response_text(cls, value: str | None) -> str | None:
        """Mask credential substrings in persisted response text."""
        return None if value is None else redact_text(value)

    @field_serializer("response_raw")
    def serialize_response(self, value: FrozenJson) -> JsonValue:
        """Thaw the immutable provider response into detached JSON."""
        return value.to_json()
