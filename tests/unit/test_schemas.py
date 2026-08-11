from datetime import UTC, datetime

import pytest
from pydantic import JsonValue, TypeAdapter, ValidationError

from hcx_eval.schemas.case import EvaluationCase
from hcx_eval.schemas.manifest import RunManifest
from hcx_eval.schemas.results import (
    ApiFamily,
    ErrorDetail,
    RawResult,
    RequestSnapshot,
    Timing,
    Usage,
)


def test_raw_result_is_immutable_and_reconciles_usage() -> None:
    # Given: a valid failed request record.
    response_raw: dict[str, JsonValue] = {"events": [{"value": "original"}]}
    record = RawResult.model_validate(
        {
            "run_id": "run-1",
            "request_id": "request-1",
            "case_id": "case-1",
            "model": "HCX-005",
            "api_family": ApiFamily.NATIVE_V3,
            "prompt_version": "v1",
            "dataset_sha256": "a" * 64,
            "docs_snapshot_sha256": "b" * 64,
            "request": RequestSnapshot.model_validate({"payload": {"messages": []}}),
            "response_raw": response_raw,
            "timing": Timing(started_at=datetime.now(UTC), e2e_ms=1.5),
            "usage": Usage(prompt_tokens=2, completion_tokens=3, total_tokens=5),
            "error": ErrorDetail(kind="timeout", message="deadline"),
        }
    )

    # When: top-level mutation is attempted and the caller mutates its source.
    with pytest.raises(ValidationError):
        record.model = "changed"
    response_raw["events"] = [{"value": "changed"}]

    # Then: the raw response retains its recursively immutable snapshot.
    assert record.model_dump(mode="json")["response_raw"] == {
        "events": [{"value": "original"}]
    }


def test_usage_rejects_inconsistent_total() -> None:
    # Given / When / Then: token totals cannot contradict their components.
    with pytest.raises(ValidationError):
        _ = Usage(
            prompt_tokens=2,
            completion_tokens=3,
            thinking_tokens=1,
            total_tokens=5,
        )


def test_timing_rejects_ttft_after_end_to_end() -> None:
    # Given / When / Then: timing chronology is enforced at the boundary.
    with pytest.raises(ValidationError):
        _ = Timing(started_at=datetime.now(UTC), ttft_ms=10, e2e_ms=5)


def test_nested_json_is_defensively_frozen_and_serializes_as_json() -> None:
    # Given: caller-owned nested lists and dictionaries for two frozen schemas.
    payload: dict[str, JsonValue] = {"messages": [{"content": "original"}]}
    metadata: dict[str, JsonValue] = {"groups": ["original"]}
    snapshot = RequestSnapshot.model_validate({"payload": payload})
    evaluation_case = EvaluationCase.model_validate(
        {
            "case_id": "case-1",
            "task": "faq",
            "prompt": "question",
            "expected": {"answers": ["original"]},
            "source_ids": ["source-1"],
            "dataset_sha256": "a" * 64,
            "metadata": metadata,
        }
    )

    # When: the caller mutates every original nested container.
    payload["messages"] = [{"content": "changed"}]
    metadata["groups"] = ["changed"]

    # Then: immutable records retain their original JSON representation.
    assert snapshot.model_dump(mode="json")["payload"] == {
        "messages": [{"content": "original"}]
    }
    assert evaluation_case.model_dump(mode="json")["metadata"] == {
        "groups": ["original"]
    }
    assert evaluation_case.model_dump(mode="json")["expected"] == {
        "answers": ["original"]
    }


def test_manifest_serialization_redacts_equals_style_cli_secrets() -> None:
    # Given: an invocation containing equals-style credential arguments.
    manifest = RunManifest(
        run_id="run-1",
        created_at=datetime.now(UTC),
        git_commit_sha="commit",
        git_dirty=False,
        python_version="3.11",
        dependency_versions=(),
        model_registry=(),
        config_sha256="a" * 64,
        dataset_sha256="b" * 64,
        docs_snapshot_sha256="c" * 64,
        max_requests=1,
        max_tokens=1,
        max_concurrency=1,
        invocation="hcx --api-key=cli-secret --authorization=auth-secret run",
    )

    # When: the manifest is serialized for persistence.
    serialized_manifest = TypeAdapter(dict[str, JsonValue]).validate_json(
        manifest.model_dump_json()
    )
    serialized = serialized_manifest["invocation"]

    # Then: credential values are masked and command structure is retained.
    assert isinstance(serialized, str)
    assert serialized == ("hcx --api-key=[REDACTED] --authorization=[REDACTED] run")
    assert "cli-secret" not in serialized
    assert "auth-secret" not in serialized
