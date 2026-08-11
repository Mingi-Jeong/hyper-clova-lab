# Result and artifact contract

Every attempted provider request is represented by the frozen `RawResult` Pydantic
schema. It identifies the run, request, case, model, API family, prompt and source
hashes; stores a recursively redacted request and response; and retains timing,
usage, HTTP/provider status, retry, and structured error data.

Artifact runs are rooted at `<results-root>/<run-id>/`. A run manifest is created
once as `manifest.json`. Raw request records are canonical, newline-terminated JSON
objects in `raw/segment-NNNNNN.jsonl`. A full or malformed final segment is never
rewritten: the next append creates a new segment. Duplicate request IDs are rejected.
Exact provider payloads, including raw `/models` responses, are created once under
`snapshots/` with a sibling SHA-256 file.

Rectangular scalar analysis rows may be exported once under `normalized/` as UTF-8
CSV. A mismatched row shape, nested value, empty table, or overwrite is rejected.

Artifact roots and run IDs are validated before directories are created. Paths may
not resolve beneath `processed-data/`, the collected NAVER documentation root, or
`.hermes/`. Secrets, API-key-like fields, bearer authorization values, cookies, and
token fields are recursively replaced with `[REDACTED]` before persistence.
