from pathlib import Path

import pytest
from pydantic import BaseModel

from hcx_eval.artifacts.writer import ArtifactError, SegmentedJsonlWriter


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
