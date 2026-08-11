from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import BaseModel, JsonValue, TypeAdapter

from hcx_eval.artifacts.writer import ArtifactError, SegmentedJsonlWriter
from hcx_eval.schemas.manifest import RunManifest
from hcx_eval.schemas.results import (
    ApiFamily,
    ErrorDetail,
    RawResult,
    RequestSnapshot,
    Timing,
)


class FixtureManifest(BaseModel):
    run_id: str


def test_writer_rotates_segments_and_rejects_duplicate_records(tmp_path: Path) -> None:
    # Given: a writer limited to one record per segment.
    writer = SegmentedJsonlWriter(tmp_path / "results", "run-1", max_records=1)

    # When: two distinct records are appended.
    first = writer.append({"request_id": "one", "value": 1})
    second = writer.append({"request_id": "two", "value": 2})

    # Then: records occupy immutable ordered segments and duplicates fail.
    assert first.name == "segment-000001.jsonl"
    assert second.name == "segment-000002.jsonl"
    with pytest.raises(ArtifactError):
        _ = writer.append({"request_id": "one", "value": 3})


def test_writer_preserves_partial_segment_and_rotates(tmp_path: Path) -> None:
    # Given: an interrupted final JSONL fragment.
    raw = tmp_path / "results" / "run-1" / "raw"
    raw.mkdir(parents=True)
    partial = raw / "segment-000001.jsonl"
    _ = partial.write_bytes(b'{"request_id":"partial"')

    # When: a new writer appends a complete record.
    written = SegmentedJsonlWriter(tmp_path / "results", "run-1").append(
        {"request_id": "complete"}
    )

    # Then: interrupted bytes are never rewritten.
    assert partial.read_bytes() == b'{"request_id":"partial"'
    assert written.name == "segment-000002.jsonl"


def test_writer_saves_exact_raw_bytes_once(tmp_path: Path) -> None:
    # Given: provider bytes whose whitespace is evidence.
    writer = SegmentedJsonlWriter(tmp_path / "results", "run-1")
    payload = b'{ "models": ["HCX-005"] }\n'

    # When: a raw snapshot is stored.
    snapshot = writer.snapshot_bytes("models-response.json", payload)

    # Then: the byte representation is unchanged and cannot be overwritten.
    assert snapshot.read_bytes() == payload
    with pytest.raises(ArtifactError):
        _ = writer.snapshot_bytes("models-response.json", b"different")


def test_writer_creates_manifest_and_normalized_csv_once(tmp_path: Path) -> None:
    # Given: a fresh run with a manifest and rectangular normalized rows.
    writer = SegmentedJsonlWriter(tmp_path / "results", "run-1")
    manifest = FixtureManifest(run_id="run-1")

    # When: both immutable artifacts are created.
    manifest_path = writer.create_manifest(manifest)
    csv_path = writer.write_normalized_csv(
        "scores.csv",
        (
            {"request_id": "one", "score": 1.0},
            {"request_id": "two", "score": 0.5},
        ),
    )

    # Then: they are parseable and neither can be replaced.
    assert '"run_id": "run-1"' in manifest_path.read_text()
    assert csv_path.read_text().splitlines() == [
        "request_id,score",
        "one,1.0",
        "two,0.5",
    ]
    with pytest.raises(ArtifactError):
        _ = writer.create_manifest(manifest)


@pytest.mark.parametrize(
    ("root", "run_id"),
    [(Path("processed-data"), "run"), (Path("results"), "../processed-data")],
)
def test_writer_rejects_protected_or_traversing_targets(
    root: Path, run_id: str
) -> None:
    # Given / When / Then: artifact destinations cannot enter protected inputs.
    with pytest.raises(ArtifactError):
        _ = SegmentedJsonlWriter(root, run_id)


def test_writer_redacts_raw_result_free_text_before_persistence(
    tmp_path: Path,
) -> None:
    # Given: a raw result with secrets in response and error free text.
    result = RawResult(
        run_id="run-1",
        request_id="request-1",
        case_id="case-1",
        model="HCX-005",
        api_family=ApiFamily.NATIVE_V3,
        prompt_version="v1",
        dataset_sha256="a" * 64,
        docs_snapshot_sha256="b" * 64,
        request=RequestSnapshot.model_validate({"payload": {"messages": []}}),
        response_text="answer before Bearer response-secret after",
        timing=Timing(started_at=datetime.now(UTC), e2e_ms=1),
        error=ErrorDetail(kind="provider", message="failed Bearer error-secret safely"),
    )

    # When: the raw result is appended through the real artifact writer.
    path = SegmentedJsonlWriter(tmp_path, "run-1").append(result)
    persisted = TypeAdapter(dict[str, JsonValue]).validate_json(path.read_bytes())

    # Then: ordinary evidence remains but neither secret reaches disk.
    assert persisted["response_text"] == ("answer before Bearer [REDACTED] after")
    persisted_error = persisted["error"]
    assert isinstance(persisted_error, dict)
    assert persisted_error["message"] == ("failed Bearer [REDACTED] safely")
    assert "response-secret" not in path.read_text()
    assert "error-secret" not in path.read_text()


def test_writer_redacts_sensitive_assignments_and_preserves_delimiters(
    tmp_path: Path,
) -> None:
    # Given: quoted and bare assignments surrounded by useful evaluation prose.
    result = RawResult(
        run_id="run-1",
        request_id="request-1",
        case_id="case-1",
        model="HCX-005",
        api_family=ApiFamily.NATIVE_V3,
        prompt_version="v1",
        dataset_sha256="a" * 64,
        docs_snapshot_sha256="b" * 64,
        request=RequestSnapshot.model_validate({"payload": {"messages": []}}),
        response_text=(
            "keep CLOVA_STUDIO_API_KEY='env secret', "
            'Api_Key="generic secret"; token=token-secret&next=visible '
            "password=pass-secret. prose api_key remains"
        ),
        timing=Timing(started_at=datetime.now(UTC), e2e_ms=1),
    )

    # When: the result crosses the append-only writer boundary.
    path = SegmentedJsonlWriter(tmp_path, "run-1").append(result)
    text = path.read_text()
    persisted = TypeAdapter(dict[str, JsonValue]).validate_json(text)
    response_text = persisted["response_text"]

    # Then: secret values vanish while quotes, delimiters, and prose remain.
    assert isinstance(response_text, str)
    assert "env secret" not in text
    assert "generic secret" not in text
    assert "token-secret" not in text
    assert "pass-secret" not in text
    assert "CLOVA_STUDIO_API_KEY='[REDACTED]'," in response_text
    assert 'Api_Key="[REDACTED]";' in response_text
    assert "token=[REDACTED]&next=visible" in response_text
    assert "password=[REDACTED]. prose api_key remains" in response_text
    assert '"inter_token_gap_p95_ms":null' in text


def test_writer_redacts_assignment_secrets_in_manifest(tmp_path: Path) -> None:
    # Given: a manifest invocation with env, generic, and CLI credentials.
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
        invocation=(
            "CloVa_Studio_Api_Key='env secret' token=token-secret "
            "hcx --authorization=auth-secret run"
        ),
    )

    # When: the manifest is persisted through the real writer.
    path = SegmentedJsonlWriter(tmp_path, "run-1").create_manifest(manifest)
    text = path.read_text()

    # Then: no assignment value reaches disk and command structure remains.
    assert all(
        secret not in text for secret in ("env secret", "token-secret", "auth-secret")
    )
    assert "CloVa_Studio_Api_Key=[REDACTED]" in text
    assert "token=[REDACTED]" in text
    assert "--authorization=[REDACTED]" in text
