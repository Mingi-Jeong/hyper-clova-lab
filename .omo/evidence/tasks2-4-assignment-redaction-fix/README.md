# Tasks 2–4 assignment-redaction fix evidence

## RED regression

- Scenario: an actual JSONL writer receives quoted/bare, mixed-case API-key,
  token, and password assignments inside response text; a real run manifest
  receives env-assignment and CLI forms.
- Invocation: targeted `pytest` for the two new writer/manifest regression tests.
- Binary observable: both tests failed before implementation because the secret
  markers reached disk; the failure output also exposed over-redaction of
  `inter_token_gap_p95_ms`.
- Artifact: `red.txt`.

## GREEN regression and repository gates

- Scenario: the same two persistence-boundary cases after the minimal redaction
  implementation.
- Invocation: targeted `pytest` invocation.
- Binary observable: `2 passed`.
- Artifact: `green.txt`.
- Scenario: all repository behavior and static-quality gates.
- Invocations: `uv run pytest -q`, `uv run ruff check .`,
  `uv run ruff format --check src tests`, and `uv run basedpyright`.
- Binary observables: `31 passed`, all Ruff checks passed, 28 files formatted,
  and zero type errors/warnings/notes.
- Artifacts: `pytest-full.txt`, `ruff-full.txt`, `format-check.txt`, and
  `basedpyright-full.txt`.
- Scenario: replay the targeted regression and every repository gate against the
  committed implementation.
- Binary observables: `2 passed`, `31 passed`, lint/format clean, and zero type
  errors/warnings/notes.
- Artifact: `post-commit-verification.txt`.
- Scenario: two direct executor stop-hook replays of the persisted boundary
  regressions, full suite, static gates, evidence presence, implementation
  identity, and protected inventories.
- Binary observables: both boundary tests pass, all 31 tests pass, static gates
  are clean, required artifacts are nonempty, and protected hashes are stable.
- Artifacts: `stop-hook-direct-verification.txt` and
  `stop-hook-direct-verification-2.txt`.
- Scenario: final executor audit proves the implementation commit is an ancestor
  of current `HEAD`, the earlier evidence blobs exist in `HEAD`, and the current
  committed tree passes boundary regressions plus every quality gate.
- Binary observables: both evidence blobs resolve, 2 boundary tests and all 31
  tests pass, with clean lint, formatting, and type analysis.
- Artifact: `stop-hook-direct-verification-3.txt`.

## Manual boundary probe

- Scenario: write a real JSONL record and manifest containing mixed-case env,
  generic, quoted, bare, and delimiter-adjacent assignments; apply redaction
  twice; retain an ordinary timing metric and prose.
- Invocation: inline `uv run python` library driver using temporary output.
- Binary observables: zero persisted leaks at both boundaries, delimiters/prose
  retained, idempotence true, and ordinary token metric retained.
- Artifact: `manual-driver.txt`.
- Scenario: protected-source read-only identity check.
- Invocation: `build_inventory` over both protected input trees.
- Binary observables: 208 data files and 2 docs files with the previously
  recorded deterministic aggregate hashes.
- Artifact: `manual-driver.txt`.

## Change hygiene

- Scenarios: Python modules stay below the 250-line ceiling and the patch has no
  whitespace errors.
- Invocations: `wc -l` and `git diff --check`.
- Binary observables: 188/211 lines and pass.
- Artifacts: `loc.txt` and `diff-check.txt`.
