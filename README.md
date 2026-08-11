# HyperCLOVA X Financial Evaluation Harness

An offline-first, reproducible harness for evaluating HyperCLOVA X models and
tools against Korean financial and pension-service tasks.

## Safety baseline

The scaffold never makes network calls. Running `hcx-eval` without a command
prints an offline status message only. Live discovery and benchmark execution
will be added in later tasks and must remain explicitly bounded by request and
budget controls.

`processed-data/` and `naver-clova-studio-instructions-all-docs/` are immutable
inputs. Create a local `.env` from `.env.example` only when live access has been
approved; `.env` is ignored by Git.

## Local checks

```bash
uv sync
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
hcx-eval --help
hcx-eval
```
