# Canonical redaction-policy fix evidence

## RED

- Scenario: every required sensitive-key family is exercised through both the
  actual segmented JSONL writer and actual run-manifest writer, with mixed case,
  quoted/bare values, and comma/semicolon/ampersand/period delimiters.
- Invocation: `uv run pytest -q tests/unit/test_artifacts.py -k canonical_sensitive_policy`.
- Binary observable: 8 failures and 28 passes; `auth`, `cookie`, `cookies`, and
  `set-cookie` leaked at both persistence boundaries.
- Artifact: `red.txt`.

## GREEN and full gates

- Scenario: the same 18-key table crosses both persistence boundaries after the
  free-text matcher delegates key decisions to the mapping policy.
- Invocation: the targeted `pytest` command above.
- Binary observable: 36 passed and 7 unrelated tests deselected.
- Artifact: `green.txt`.
- Scenario: complete regression and static-quality gates.
- Invocations: `uv run pytest -q`, `uv run ruff check .`,
  `uv run ruff format --check src tests`, and `uv run basedpyright`.
- Binary observables: 65 passed, Ruff clean, 28 files formatted, and zero type
  errors/warnings/notes.
- Artifacts: `pytest-full.txt`, `ruff-full.txt`, `format-check.txt`, and
  `basedpyright-full.txt`.
- Scenario: replay the boundary table, full suite, and all static gates against
  the committed implementation.
- Binary observables: 36 boundary cases and all 65 tests pass, with clean lint,
  formatting, and type analysis.
- Artifact: `post-commit-verification.txt`.
- Scenario: direct executor stop-hook replay against the stable implementation
  commit, including boundary tests, all gates, a sensitive/ordinary policy table,
  and protected inventories.
- Binary observables: 36 boundary cases and all 65 tests pass; 17 canonical
  policy and seven ordinary-preservation checks agree; protected hashes match.
- Artifact: `stop-hook-direct-verification.txt`.
- Scenario: second executor replay verifies the implementation ancestor and first
  evidence blob in `HEAD` before rerunning boundary and complete repository gates.
- Binary observables: ancestry and blob checks pass, 36 boundary cases pass, all
  65 tests pass, and static gates remain clean.
- Artifact: `stop-hook-direct-verification-2.txt`.
- Scenario: terminal executor audit verifies both earlier evidence blobs and the
  implementation ancestor before one final replay of boundary and full gates.
- Binary observables: ancestry and both blobs resolve, 36 boundary cases and all
  65 tests pass, with clean lint, formatting, and type analysis.
- Artifact: `stop-hook-direct-verification-3.txt`.

## Manual property-style persistence table

- Scenario: 18 canonical key/case/quote/delimiter combinations are written to
  both JSONL and manifests; seven ordinary assignment/prose cases are retained;
  redaction is reapplied to prove idempotence.
- Invocation: inline `uv run python` driver with isolated temporary output.
- Binary observables: 18 writer checks, 18 manifest checks, mapping/free-text
  consistency true, ordinary assignments retained, and idempotence true.
- Artifact: `manual-property-table.txt`.
- Scenario: protected-source identity remains unchanged.
- Invocation: `build_inventory` for both protected roots in the manual driver.
- Binary observables: 208 data files and 2 documentation files retain their
  recorded aggregate SHA-256 hashes.
- Artifact: `manual-property-table.txt`.

## Hygiene and audit note

- Scenarios: changed Python files remain below 200 pure lines and the patch has
  no whitespace errors.
- Invocations: pure-line `awk` count and `git diff --check`.
- Artifacts: `pure-loc.txt` and `diff-check.txt`.
- The optional no-excuse audit reports three inherited `missing-assert-never`
  findings on scalar catch-all match arms. Adding unreachable arms makes strict
  basedpyright fail, so the authoritative zero-finding type gate is retained.
  The exact diagnostic and nonzero exit are in `no-excuse-audit-final.txt`.
