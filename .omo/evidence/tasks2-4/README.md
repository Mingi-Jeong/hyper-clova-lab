# Tasks 2-4 evidence

## Automated scenarios

- Scenario: configuration, redaction, inventory, registry, schemas, IDs, and
  artifact persistence. Invocation: `uv run pytest -q`. Binary observable:
  exit 0 with 25 passing tests. Artifact: `pytest-full.txt`.
- Scenario: all repository Python lint rules. Invocation: `uv run ruff check .`.
  Binary observable: exit 0 and `All checks passed!`. Artifact: `ruff-full.txt`.
- Scenario: repository formatting. Invocation: `uv run ruff format --check src
  tests`. Binary observable: exit 0 and 28 files already formatted. Artifact:
  `format-check.txt`.
- Scenario: strict static typing. Invocation: `uv run basedpyright`. Binary
  observable: 0 errors. Artifact: `basedpyright-full.txt` (final rerun after
  implementation).

## Red-green evidence

- Initial missing boundaries: `red-targeted.txt`; targeted green:
  `green-targeted.txt`.
- Deterministic IDs: `red-ids.txt`; green: `green-ids.txt`.
- Normalized export: `red-normalized-export.txt`; green:
  `green-normalized-export.txt`.

## Manual library scenario

Invocation: the offline `uv run python` driver captured in `manual-driver.txt`.
Binary observables: environment precedence `6`, execution `false`, nested
Authorization redacted, 208 source files hashed twice unchanged, two official
snapshot files hashed twice unchanged, 31 documents and nine documented model
identifiers parsed, JSONL rotated into two segments, duplicate ID rejected,
protected target rejected, and raw snapshot bytes retained with SHA-256 sidecar.
Deterministic UUID identities and the create-once normalized CSV surface were
driven separately in `manual-ids-csv.txt`.

Protected-source manifests observed unchanged during the driver:

- `processed-data/`: 208 files, 28,368,002 bytes,
  `869e3c3db5c8a2f46b377b0739af2adb14ef4e0e22f01b59ab0828aea7253fb6`.
- Official docs root: 2 files, 468,392 bytes,
  `33efc2ad7f87187b3b667542da874eb4cea88e59d0e2b3c9158837460c48b9a2`.
- Official JSON snapshot:
  `f248d6c5a0034b82b5b4144fb0e32119d8f311e4e5c01241d3e66d02bf81b6bb`.

Additional artifacts: `.env` ignore proof in `env-ignore.txt`, file-size gate in
`loc.txt`, and whitespace/conflict proof in `diff-check.txt`.
