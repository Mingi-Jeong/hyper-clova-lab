"""Append-only segmented JSONL and byte-exact snapshot persistence."""

import csv
import fcntl
import hashlib
import io
import json
import os
import re
from collections.abc import Generator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pydantic import BaseModel, JsonValue, TypeAdapter
from typing_extensions import override

from hcx_eval.security import redact_mapping

_RUN_ID_PATTERN: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SNAPSHOT_PATTERN: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_JSON_OBJECT: Final = TypeAdapter(dict[str, JsonValue])
_PROTECTED_NAMES: Final = {
    ".hermes",
    "naver-clova-studio-instructions-all-docs",
    "processed-data",
}


@dataclass(slots=True)
class ArtifactError(ValueError):
    """Mutable exception because Python assigns traceback state during propagation."""

    path: Path
    reason: str

    @override
    def __str__(self) -> str:
        """Render the artifact path and safe reason."""
        return f"unsafe artifact operation at {self.path}: {self.reason}"


class SegmentedJsonlWriter:
    """Append records into immutable, interruption-tolerant JSONL segments."""

    def __init__(self, root: Path, run_id: str, *, max_records: int = 1000) -> None:
        """Validate the destination without creating artifacts."""
        resolved_root = root.resolve()
        if any(part in _PROTECTED_NAMES for part in resolved_root.parts):
            raise ArtifactError(path=root, reason="target is beneath a protected root")
        if _RUN_ID_PATTERN.fullmatch(run_id) is None:
            raise ArtifactError(path=Path(run_id), reason="invalid run id")
        if max_records <= 0:
            raise ArtifactError(path=root, reason="segment capacity must be positive")
        self._run_root: Path = resolved_root / run_id
        self._raw_root: Path = self._run_root / "raw"
        self._snapshot_root: Path = self._run_root / "snapshots"
        self._max_records: int = max_records

    @contextmanager
    def _locked(self) -> Generator[None, None, None]:
        self._run_root.mkdir(parents=True, exist_ok=True)
        lock_path = self._run_root / ".append.lock"
        with lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _segments(self) -> list[Path]:
        return sorted(self._raw_root.glob("segment-*.jsonl"))

    @staticmethod
    def _records(path: Path) -> tuple[list[dict[str, JsonValue]], bool]:
        raw = path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            return [], False
        try:
            records = [_JSON_OBJECT.validate_json(line) for line in raw.splitlines()]
        except ValueError:
            return [], False
        return records, True

    def append(self, record: BaseModel | Mapping[str, JsonValue]) -> Path:
        """Append one redacted record, rotating rather than repairing bad tails."""
        if isinstance(record, BaseModel):
            parsed = _JSON_OBJECT.validate_python(record.model_dump(mode="json"))
        else:
            parsed = _JSON_OBJECT.validate_python(dict(record))
        safe_record = redact_mapping(parsed)
        request_id = safe_record.get("request_id")
        if not isinstance(request_id, str) or not request_id:
            raise ArtifactError(path=self._run_root, reason="request_id is required")
        encoded = (
            json.dumps(
                safe_record,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode()
            + b"\n"
        )

        with self._locked():
            self._raw_root.mkdir(parents=True, exist_ok=True)
            segments = self._segments()
            last_records: list[dict[str, JsonValue]] = []
            last_valid = False
            for segment in segments:
                records, valid = self._records(segment)
                duplicate = any(
                    item.get("request_id") == request_id for item in records
                )
                if valid and duplicate:
                    raise ArtifactError(path=segment, reason="duplicate request_id")
                if segment == segments[-1]:
                    last_records, last_valid = records, valid
            if segments and last_valid and len(last_records) < self._max_records:
                target = segments[-1]
            else:
                target = self._raw_root / f"segment-{len(segments) + 1:06d}.jsonl"
            descriptor = os.open(
                target,
                os.O_APPEND | os.O_CREAT | os.O_WRONLY,
                0o600,
            )
            try:
                view = memoryview(encoded)
                while view:
                    written = os.write(descriptor, view)
                    view = view[written:]
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return target

    def create_manifest(self, manifest: BaseModel) -> Path:
        """Create the immutable run manifest exactly once."""
        payload = (
            manifest.model_dump_json(indent=2, exclude_none=False).encode() + b"\n"
        )
        return self._write_once(self._run_root / "manifest.json", payload)

    def write_normalized_csv(
        self, name: str, rows: Sequence[Mapping[str, JsonValue]]
    ) -> Path:
        """Create one rectangular normalized CSV table without overwrite."""
        if _SNAPSHOT_PATTERN.fullmatch(name) is None or not name.endswith(".csv"):
            raise ArtifactError(path=Path(name), reason="invalid CSV name")
        if not rows:
            raise ArtifactError(path=Path(name), reason="CSV rows are required")
        safe_rows = tuple(redact_mapping(row) for row in rows)
        fieldnames = tuple(safe_rows[0])
        if not fieldnames or any(tuple(row) != fieldnames for row in safe_rows):
            raise ArtifactError(path=Path(name), reason="CSV rows must be rectangular")
        if any(
            isinstance(value, (dict, list))
            for row in safe_rows
            for value in row.values()
        ):
            raise ArtifactError(path=Path(name), reason="CSV values must be scalar")
        output = io.StringIO(newline="")
        table = csv.writer(output, lineterminator="\n")
        table.writerow(fieldnames)
        table.writerows(tuple(row[field] for field in fieldnames) for row in safe_rows)
        payload = output.getvalue().encode()
        return self._write_once(self._run_root / "normalized" / name, payload)

    def snapshot_bytes(self, name: str, payload: bytes) -> Path:
        """Store exact provider bytes and a SHA-256 sidecar without overwrite."""
        if _SNAPSHOT_PATTERN.fullmatch(name) is None:
            raise ArtifactError(path=Path(name), reason="invalid snapshot name")
        snapshot = self._write_once(self._snapshot_root / name, payload)
        digest = hashlib.sha256(payload).hexdigest().encode() + b"\n"
        _ = self._write_once(snapshot.with_suffix(snapshot.suffix + ".sha256"), digest)
        return snapshot

    def _write_once(self, path: Path, payload: bytes) -> Path:
        with self._locked():
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError as error:
                raise ArtifactError(
                    path=path, reason="artifact already exists"
                ) from error
            try:
                view = memoryview(payload)
                while view:
                    written = os.write(descriptor, view)
                    view = view[written:]
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return path
