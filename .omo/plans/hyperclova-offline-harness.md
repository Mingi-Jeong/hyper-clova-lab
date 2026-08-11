# HyperCLOVA X offline harness

Authoritative handoff: `.hermes/plans/2026-08-12_025142-codex-hyperclova-evaluation-handoff.md`.
Protected inputs are `processed-data/` and
`naver-clova-studio-instructions-all-docs/`.

- [x] 1. Initialize safe project scaffolding and an offline-safe CLI.
- [x] 2. Implement validated configuration and secret redaction.
- [x] 3. Implement source inventory and immutable snapshot hashing.
- [x] 4. Define schemas and append-safe artifact writer.
- [x] 5. Implement native and OpenAI-compatible clients (independent security review PASS at `994a1ec`).
- [x] 6. Implement model discovery and capability probes (independent security review PASS at `994a1ec`).
- [x] 7. Build deterministic evaluation cases.
- [x] 8. Implement scoring metrics.
- [x] 9. Implement smoke and baseline generation runners.
- [x] 10. Implement precise latency runner.
- [x] 11. Implement embeddings and API-tool evaluation.
- [x] 12. Add capability-specific generation tracks.
- [x] 13. Add synthetic financial safety red-team.
- [x] 14. Implement report generators.
- [x] 15. Write runbook and verify offline.
- [ ] 16. User-key live discovery and smoke test (requires user approval and injected key).
