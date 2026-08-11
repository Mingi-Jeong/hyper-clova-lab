"""Deterministic run and request identity construction."""

import json
import uuid
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class RunIdentity(BaseModel):
    """Inputs whose equality defines the same reproducible run identity."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    run_seed: str = Field(min_length=1)
    config_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dataset_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    docs_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class RequestIdentity(BaseModel):
    """Inputs whose equality defines one provider request attempt."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    run_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    model: str = Field(min_length=1)
    model_mode: str | None = None
    attempt: int = Field(ge=0)


def _canonical_identity(identity: BaseModel) -> str:
    return json.dumps(
        identity.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def make_run_id(identity: RunIdentity) -> str:
    """Derive a stable UUID run ID from all reproducibility inputs."""
    return f"run-{uuid.uuid5(uuid.NAMESPACE_URL, _canonical_identity(identity))}"


def make_request_id(identity: RequestIdentity) -> str:
    """Derive a stable UUID request ID while distinguishing retries."""
    return str(uuid.uuid5(uuid.NAMESPACE_OID, _canonical_identity(identity)))
