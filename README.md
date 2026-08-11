# HyperCLOVA X Financial Evaluation Harness

An offline-first, reproducible harness for evaluating HyperCLOVA X models and
API tools on Korean financial and pension-service tasks. It keeps
OpenAI-compatible, native v1, and native v3 wire contracts separate, retains
failed calls as evidence, and never turns a missing result into an estimated
score.

## Safety baseline

- `inventory`, `build-cases`, `report`, and every default dry-run are local-only.
- `discover`, `smoke`, and baseline generation require both `--execute` and
  `EXECUTE=true`, plus positive request/token ceilings and an injected key.
- Specialized `latency`, `embeddings`, `api-tools`, and `safety` phases expose
  bounded preflights, but live execution is deliberately blocked before the
  approved post-smoke workflow.
- `.env`, credentials, and authorization values are ignored and redacted.
- `processed-data/`, `naver-clova-studio-instructions-all-docs/`, and
  `docs/model-evaluation/` are read-only inputs.

No real CLOVA request is needed for development or verification.

## Setup and checks

```bash
uv sync --frozen
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
uv run hcx-eval --help
```

## Offline workflow

```bash
uv run hcx-eval inventory
uv run hcx-eval build-cases --dataset structured
uv run hcx-eval discover --dry-run
uv run hcx-eval smoke --max-requests 20 --dry-run
uv run hcx-eval run --phase faq --models all --max-requests 100 --dry-run
uv run hcx-eval run --phase safety --max-requests 100 --dry-run
uv run hcx-eval report --run-id <RUN_ID>
```

`report` reads
`results/<RUN_ID>/normalized/report-bundle.json` unless `--bundle` is supplied.
It writes separate factual and pension-service insight reports once. See
[the runbook](docs/implementation/RUNBOOK.md) for live preconditions, resume,
request accounting, and cleanup, and
[the architecture](docs/implementation/ARCHITECTURE.md) for trust boundaries.
