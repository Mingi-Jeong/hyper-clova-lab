# Actual Test Results — offline-fixture

State legend: `NOT_RUN`, `UNSUPPORTED`, `UNAVAILABLE`, `RATE_LIMITED`, and `INSUFFICIENT_N` are evidence states, not zero scores.

## 1. Executive factual summary

- No live provider request was made. Evidence: [manifest](../../offline-fixture/manifest.json)

## 2. Scope and exclusions

Scope:

- offline mock validation

Exclusions:

- live CLOVA API

## 3. Environment and reproducibility manifest

Manifest: [manifest](../../offline-fixture/manifest.json)

## 4. Model/API availability

### 9.1 Model availability and capabilities

| Model | Discovery source | Status | API family | Text | Vision | Thinking | Structured Outputs | Function calling | Context/output limits | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HCX-FIXTURE | mock registry | UNAVAILABLE | openai-compatible | NOT_RUN | UNSUPPORTED | NOT_RUN | NOT_RUN | NOT_RUN | unknown | manifest |

Evidence: [manifest](../../offline-fixture/manifest.json)

## 5. Dataset and case counts

See the manifest and table evidence. Missing counts remain `NOT_RUN`; they are never inferred.

## 6. Quality scorecards with confidence intervals

### 9.2 Overall generation-model scorecard

| Model/config | Accuracy 20 | RAG 15 | Reasoning 15 | Safety 20 | Instruction 10 | Korean 5 | Operations 15 | Total | Gate | Grade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

Evidence: [manifest](../../offline-fixture/manifest.json)

### 9.3 Dataset/task quality

| Model/config | Task | N | Accuracy/EM/F1 | Fact recall | Contradiction | Unsupported claim | 95% CI | Key failure IDs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

Evidence: [manifest](../../offline-fixture/manifest.json)

### 9.4 Grounding and citations

| Model/retrieval | Recall@5 | MRR@10 | nDCG@10 | Citation precision | Citation recall | Faithfulness | Unsupported claims | Added latency p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

Evidence: [manifest](../../offline-fixture/manifest.json)

### 9.5 Structured output and tools

| Model/mode | JSON parse | Schema valid | Required fields | Tool name accuracy | Argument F1 | Unneeded calls | Tool-result faithfulness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

Evidence: [manifest](../../offline-fixture/manifest.json)

## 7. Latency and load results

### 9.7 Latency and operations

| Model/config/load | N | TTFT p50/p95/p99 | E2E p50/p95/p99 | TPOT p50/p95 | Gap p95/p99 | Max stall | tok/s | Timeout | 429 | 5xx | Cost/request | Cost/correct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

Evidence: [manifest](../../offline-fixture/manifest.json)

### 9.8 Embedding and API-tool scorecard

| Model/API | Task | Quality metric | Latency p50/p95/p99 | Throughput | Error rate | Incremental E2E latency | Strengths | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

Evidence: [manifest](../../offline-fixture/manifest.json)

## 8. Safety hard-gate results

### 9.6 Safety

| Model/config | PII leak | Guarantee claim | Fabrication | Injection success | Unsafe advice | Over-refusal | Gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

Evidence: [manifest](../../offline-fixture/manifest.json)

## 9. Cost/token usage with source date

Cost basis: unknown. Unknown pricing is not estimated.

## 10. Per-model strengths and reproducible failure cases

Only evidence-linked facts in the tables above are reportable. Unlinked narrative is intentionally omitted.

## 11. Statistical comparisons and Pareto frontier

NOT_RUN — no measured quality/latency/cost points were supplied.

## 12. Limitations and invalid/incomplete cells

Every incomplete cell uses an explicit state. No missing measurement is converted to a plausible number.

## 13. Raw artifact index and exact reproduction commands

Primary evidence: [manifest](../../offline-fixture/manifest.json)

```text
uv run hcx-eval report --run-id offline-fixture
```
