# Tasks 2-4 review-fix evidence

Review blockers were reproduced from `.omo/evidence/tasks2-4-code-review.md` and
fixed without changing protected inputs.

- RED: `uv run pytest -q tests/unit/test_security.py tests/unit/test_schemas.py
  tests/unit/test_artifacts.py`; missing `redact_text` boundary recorded in
  `red.txt`.
- Targeted GREEN: the same invocation passed 15 scenarios in `green.txt`, covering
  embedded Bearer values, both equals-style CLI credential flags, ordinary-content
  preservation, defensive deep freezing, manifest serialization, and persisted
  RawResult JSONL.
- Full suite: `pytest-full.txt` records 29 passed; `ruff-full.txt`,
  `format-check.txt`, and `basedpyright-full.txt` record clean static gates.
- Manual library driver: `manual-driver.txt` records rejected nested mutation,
  detached caller-owned containers, secret-free RawResult and manifest bytes,
  preserved ordinary response content, and redacted structured logging fields.
- `diff-check.txt` and `loc.txt` record patch hygiene and the source-size gate.
