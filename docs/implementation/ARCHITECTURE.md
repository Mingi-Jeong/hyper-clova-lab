# Harness architecture

## Design intent

The harness turns immutable source material and bounded provider observations
into traceable evaluation records. Local planning is the default. Network
dispatch exists only behind two independent approvals: a CLI `--execute` flag
and validated configuration with `EXECUTE=true`, a key, and positive ceilings.

```text
read-only sources ──> inventory/case builders ──> reviewed cases
official docs ──────> documented registry ─┐
mock or live /models ─> observed registry ─┴─> bounded plans
                                            ├─> generation / latency
                                            ├─> embeddings / API tools
                                            ├─> isolated capabilities
                                            └─> synthetic safety
raw append-only evidence ─> deterministic metrics ─> normalized report bundle
                                                   ├─> ACTUAL_TEST_RESULTS.md
                                                   └─> FINANCIAL_PENSION_MODEL_INSIGHTS.md
```

## Trust boundaries

The following roots are inputs and must not be modified:

- `processed-data/`
- `naver-clova-studio-instructions-all-docs/`
- `docs/model-evaluation/`
- the authoritative handoff under `.hermes/plans/`

Generated cases live under `cases/generated/`; reviewed synthetic fixtures live
under `cases/reviewed/`; run output lives under ignored `results/`. Writers use
exclusive creation or append-only segments so an existing observation is not
silently replaced.

Untrusted provider data is validated at the adapter boundary. Request headers,
payloads, response bodies, free text, errors, provider status codes, and report
text pass through credential redaction before persistence. Synthetic PII is
masked before red-team results leave the runner.

## Protocol separation

The three generation adapters deliberately do not share request/response wire
models:

| Adapter | Contract | Main implementation |
| --- | --- | --- |
| OpenAI-compatible | `/models`, chat, embeddings, SSE | `clients/openai_compat.py` |
| Native v1 | v1 message and result fields | `clients/native_v1.py` |
| Native v3 | v3 message, usage, and feature fields | `clients/native_v3.py` |

`AdapterGenerationBackend` routes an already planned job to exactly one adapter.
Model-specific Thinking, Structured Outputs, function calling, vision, and
context-limit tests remain isolated cells. An unsupported capability is evidence
(`UNSUPPORTED`), not a quality failure and not a reason to retry blindly.

## Reproducibility and failure semantics

Every complete live run is expected to pin the Git state, environment, model
registry, raw model response, capability evidence, dataset and documentation
hashes, prompts, request ceilings, concurrency, and price basis. Per-request
JSONL is segmented and append-safe. Resume derives stable request IDs and skips
records already present; failures stay in the dataset and in latency/error-rate
denominators.

Metrics are deterministic unless a seeded bootstrap is requested. TTFT, E2E,
TPOT, token gaps, and stalls derive from one monotonic client clock. Warm-up
attempts are labeled, not discarded from the audit record.

## Reporting boundary

`ReportBundle` is the normalized, validated interface to reporting. It requires
all nine scorecard tables and table-level artifact links. Missing measurements
must be one of the explicit states such as `NOT_RUN`, `UNSUPPORTED`,
`UNAVAILABLE`, `RATE_LIMITED`, or `INSUFFICIENT_N`.

The factual report contains observations and reproduction links. The pension
insight report contains downstream interpretation, routing guidance, and the
required compliance chain:

`Input Guard → Agent Trace → Output Guard → Audit Trail`

The two files are intentionally never collapsed into one marketing summary.
