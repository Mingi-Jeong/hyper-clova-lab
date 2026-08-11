# Financial/Pension Model Insights — offline-fixture

This file contains interpretation and architecture guidance. Empirical measurements remain in `ACTUAL_TEST_RESULTS.md`.

## 1. What the measurements imply for a pension Agent architecture

- Model routing remains undecided until a live run. Evidence: [manifest](../../offline-fixture/manifest.json)

## 2. Recommended model routing by pension use case

### 9.9 Pension-service routing recommendation

| Pension use case | Recommended model/API | Fallback | Required RAG | Required Guard | Target SLO | Evidence | Prohibited/unsafe use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

Evidence: [manifest](../../offline-fixture/manifest.json)

Routing is task-specific; this report does not force a single model winner.

## 3. RAG, reranker, citation, calculator, and rule-engine requirements

Use reviewed retrieval evidence and citations for pension claims. Keep calculations and eligibility rules in deterministic, versioned services; do not delegate them solely to generation.

## 4. Compliance-first deployment requirements

Required control chain: **Input Guard → Agent Trace → Output Guard → Audit Trail**. A failed safety hard gate blocks customer-facing deployment regardless of weighted quality.

## 5. Customer-facing versus internal/PB/human-in-the-loop suitability

`NOT_RUN` or failed-gate configurations are not customer-facing candidates. Internal/PB use still requires source display, review, and audit retention.

## 6. Latency budgets and degradation/fallback strategies

Set SLOs only from warm, cold, and load-specific client measurements. On timeout, rate limit, or provider failure, degrade to source retrieval or a human handoff without fabricating an answer.

## 7. Vision use for prospectus tables and scans

Vision support is an isolated capability. Require reviewed PNG fixtures, OCR/table verification, and source-page citation before using extracted values.

## 8. Structured output and function-calling implications

Use schema validation and tool allowlists. Unsupported combinations remain `UNSUPPORTED`, and malformed arguments must never reach financial actions.

## 9. Cost/quality/latency trade-offs

Cost basis: unknown. Pareto charts: NOT_RUN.

## 10. Known failure modes and prohibited uses

Prohibit guaranteed-return claims, unsuitable personalized advice, fabricated laws/products/sources, PII disclosure, prompt-injection leakage, and autonomous transaction execution.

## 11. Recommended production proof-of-concept configuration

Do not select a production model from `NOT_RUN` cells. A future proof of concept must pin the model registry, retrieval corpus, prompts, rule engine, guards, request ceilings, and evidence manifest.

## 12. Next experiments required before a real financial-service build

Run approved discovery and bounded smoke first, then reviewed quality, safety, latency/load, embedding, and API-tool phases. Re-generate both reports and require human compliance review.

Evidence root: [manifest](../../offline-fixture/manifest.json)
