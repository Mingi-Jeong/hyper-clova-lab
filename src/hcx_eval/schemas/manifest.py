"""Reproducibility manifest schema."""

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_serializer

from hcx_eval.schemas.model import ModelRecord


class RunManifest(BaseModel):
    """Immutable environment and input identity for one bounded run."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    run_id: str = Field(min_length=1)
    created_at: datetime
    git_commit_sha: str = Field(min_length=1)
    git_dirty: bool
    python_version: str = Field(min_length=1)
    dependency_versions: tuple[str, ...]
    model_registry: tuple[ModelRecord, ...]
    models_response_path: str | None = None
    config_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    docs_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    max_requests: int = Field(gt=0)
    max_tokens: int = Field(gt=0)
    max_concurrency: int = Field(gt=0)
    price_basis: str = "unknown"
    invocation: str = Field(min_length=1)
    api_key: SecretStr | None = Field(default=None, exclude=True)

    @field_serializer("invocation")
    def serialize_invocation(self, invocation: str) -> str:
        """Mask credential-bearing command arguments."""
        parts = invocation.split()
        redacted: list[str] = []
        mask_next = False
        for part in parts:
            if mask_next:
                redacted.append("[REDACTED]")
                mask_next = False
            elif part.casefold() in {"--api-key", "--authorization"}:
                redacted.append(part)
                mask_next = True
            else:
                redacted.append(part)
        return " ".join(redacted)
