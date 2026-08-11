# Offline and bounded-run runbook

## 1. Prepare the workspace

Use Python 3.11 through `uv` and install exactly the locked environment:

```bash
uv sync --frozen
uv run hcx-eval --help
```

Confirm the four source packages are present before continuing. Treat them as
read-only:

```bash
uv run hcx-eval inventory
```

The expected source identities for this handoff are:

| Root | Files | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `processed-data/` | 208 | 28,368,002 | `869e3c3db5c8a2f46b377b0739af2adb14ef4e0e22f01b59ab0828aea7253fb6` |
| `naver-clova-studio-instructions-all-docs/` | 2 | 468,392 | `33efc2ad7f87187b3b667542da874eb4cea88e59d0e2b3c9158837460c48b9a2` |
| `docs/model-evaluation/` | 7 | 41,019 | `a587d787bdcd4c55fe0631f0e3ceeb687b8054618d6ca3be76d084a46e475828` |

Stop if any identity differs unexpectedly. Do not repair an input in place.

## 2. Configure without exposing credentials

Do not commit `.env`. If a future approved live step is needed, copy the field
names from `.env.example` and enter the key locally yourself. Never paste the key
into a command, shell history, issue, report, or chat transcript.

Network execution requires all of the following:

1. the command's explicit `--execute` switch;
2. `EXECUTE=true` in the effective environment;
3. a non-empty `CLOVA_STUDIO_API_KEY`;
4. positive `MAX_REQUESTS_PER_RUN` and `MAX_TOKENS_PER_RUN`;
5. a CLI request ceiling no larger than the configured ceiling.

Keep `EXECUTE=false` for all offline work. Do not inspect or print `.env` to
verify it; use dry-run behavior and the fixed validation errors instead.

## 3. Build cases locally

```bash
uv run hcx-eval build-cases \
  --dataset structured \
  --data-root processed-data \
  --output cases/generated/structured.jsonl
```

The current deterministic bundle contains 352 cases and has SHA-256
`d65159c3775da26eb8489a60c9aa663f9fe70b3d8d4237da0bd1a0e8cbe2427d`.
Generated paraphrases remain `unreviewed`; they are not gold labels.

## 4. Preflight discovery and smoke

Both commands are dry-run by default:

```bash
uv run hcx-eval discover --dry-run --max-requests 1
uv run hcx-eval smoke \
  --registry results/model-registry.json \
  --run-id smoke-preflight \
  --max-requests 20 \
  --max-tokens 8 \
  --dry-run
```

The discovery preflight must say `planned_requests=1` and
`external_requests=0`. Smoke prints the complete eligible generation-model set,
request count, ceiling, and `external_requests=0`; it fails instead of
truncating an oversized plan.

Task 16 and real CLOVA calls are not part of the current implementation run. At
the later approval gate, discovery would use exactly one GET `/models` request.
Smoke would then use one minimal text request for each live generation model,
while the embedding, capability, and API-tool phases cover the rest of the
discovered model families.

## 5. Preflight benchmark phases

Baseline generation selects source task names (`faq`, `transfer-code`, or
`transfer-reason`) and remains dry-run unless explicitly executed:

```bash
uv run hcx-eval run \
  --run-id example-run \
  --phase faq \
  --models all \
  --max-requests 100 \
  --max-tokens 256 \
  --dry-run
```

Specialized runners expose exact offline request accounting:

```bash
uv run hcx-eval run --phase latency --max-requests 100 --dry-run
uv run hcx-eval run --phase embeddings --max-requests 100 --dry-run
uv run hcx-eval run --phase api-tools --max-requests 100 --dry-run
uv run hcx-eval run --phase safety --max-requests 100 --dry-run
```

Latency counts each warm-up and measured attempt. Embeddings count every reviewed
document and query per eligible model. API tools count eligible isolated tool
stages. Safety counts seven reviewed synthetic cases per live generation model.
These specialized CLI phases deliberately reject `--execute` at the current
Task 16 boundary; run full benchmarks only after discovery, smoke, scope review,
and a separate approval. Taken together, the baseline, capability, embedding,
and safety phases are intended to cover every discovered model family.

Do not mix specialized and generation phases in one command. Separate runs make
protocol, failure, and cost attribution defensible.

## 6. Resume safely

Use the identical `--run-id`, registry, cases, phases, model selectors, token
limit, and source hashes. The generation writer derives deterministic request
IDs, skips complete records, appends new segments, and never overwrites an
existing result. Inspect the manifest and preflight again before resuming; a
changed scope should receive a new run ID.

An interrupted or malformed segment is retained. Do not edit it. The next append
rotates to a new segment so forensic evidence remains available.

## 7. Generate reports

Aggregation must first produce a validated normalized bundle at:

```text
results/<RUN_ID>/normalized/report-bundle.json
```

Then run:

```bash
uv run hcx-eval report --run-id <RUN_ID>
```

To use an explicit local bundle:

```bash
uv run hcx-eval report \
  --run-id <RUN_ID> \
  --bundle <BUNDLE_PATH> \
  --results-root results
```

Outputs are write-once:

- `results/reports/<RUN_ID>/ACTUAL_TEST_RESULTS.md`
- `results/reports/<RUN_ID>/FINANCIAL_PENSION_MODEL_INSIGHTS.md`
- zero or two Pareto SVGs under `charts/`, depending on measured points

Every aggregate table needs artifact references. A missing result must remain an
explicit state, never a guessed value.

## 8. Verify offline

```bash
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
uv run hcx-eval --help
uv run hcx-eval inventory
uv run hcx-eval discover --dry-run
```

The mock end-to-end test performs model discovery and one smoke generation only
through `httpx2.MockTransport`, writes raw/registry/run artifacts, generates both
reports, and audits every output for the fixture credential marker:

```bash
uv run pytest -q tests/integration/test_offline_e2e.py
```

## 9. Request accounting and stop point

For the later smallest live validation, define:

- `G`: live generation models selected for one minimal smoke request each;
- `E`: live embedding models selected for one minimal embedding request each;
- `C`: approved model/capability probe cells, each isolated.

The expected count is `1 + G + E + C`: one discovery request plus the selected
smoke, embedding, and capability cells. Retries consume the same hard budget and
must be included in configured ceilings. Determine the exact values from the
fresh discovery registry and dry-run; do not estimate model availability.

Stop after dry-run and mock verification. Before any real call, report the exact
models, cells, maximum requests, maximum tokens, retry allowance, and expected
cost basis, then obtain explicit user approval.

## 10. Cleanup and archival

`results/` is ignored by Git, but write-once behavior means reusing a run ID will
fail. Inspect the exact run directory first. Archive or move that single named
directory outside the workspace; never recursively clean a wildcard, repository
root, protected input root, or unresolved environment-variable path.

Before committing, verify:

```bash
git status --short --ignored
git diff --check
git ls-files .env
```

The last command must produce no output. Do not include raw provider artifacts or
reports in Git unless they have been reviewed, redacted, and deliberately
selected for retention.
