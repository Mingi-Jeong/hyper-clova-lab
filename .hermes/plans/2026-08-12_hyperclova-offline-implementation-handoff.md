# HyperCLOVA 오프라인 평가 하네스 구현 핸드오프

기준 시각: 2026-08-12 (Asia/Shanghai)
기준 커밋: `c5a596a71fe6679dadf52883d90485ee1c6c87cd` (`fix: redact provider failure evidence`)
권위 있는 원 계획: `.hermes/plans/2026-08-12_025142-codex-hyperclova-evaluation-handoff.md`

## 1. 재개 지점과 판단 기준

목표는 한국 금융·연금 업무용 HyperCLOVA X 모델/API를 **재현 가능하고
비용이 통제된 방식으로 평가**하는 하네스를 완성하는 것이다. 최종 산출물은
실측 결과 보고서와 금융·연금 서비스 인사이트 보고서를 분리해야 한다.

아래 용어를 엄격히 구분한다.

- **직접 검증됨**: 이 핸드오프 작성 중 현재 `HEAD`에서 명령을 실행해 확인했다.
- **기존 기록**: `.omo/evidence/`의 과거 산출물이 주장하는 내용이다. 유용하지만
  이 문서가 독립적으로 재실행하지 않은 부분은 그대로 확정 사실로 취급하지 않는다.
- **미실행**: 실제 CLOVA 자격 증명과 네트워크를 사용하는 호출 또는 그 결과가 없다.

### 절대 안전 규칙

- `processed-data/`와 `naver-clova-studio-instructions-all-docs/`는 읽기 전용
  보호 입력이다. 수정·이동·정규화·삭제하지 않는다.
- `.env`, API 키, Authorization/Cookie 헤더, 자격 증명 값, 원문 비밀값을 출력,
  커밋, 보고서, raw artifact에 넣지 않는다. 이 문서에는 환경변수 **이름만** 쓴다.
- `execute=false`, 양수 요청/토큰 상한, 승인된 사용자 키가 모두 갖춰지기 전에는
  네트워크 요청을 보내지 않는다. 전체/고동시성/유료 벤치마크, 튜닝 작업,
  외부 공개는 사용자 명시 승인 전 금지다.
- 새 결과는 새 run ID/디렉터리에 append-safe로 남기며 과거 raw 결과를 덮어쓰거나
  삭제하지 않는다. 실제 PII 대신 합성·마스킹된 테스트 데이터만 쓴다.

## 2. 현재 상태 요약

구현 범위 **Task 1–6의 코드와 목 테스트 범위는 존재하며**, 상태 파일은 Task 5–6을
완료된 구현 범위로 정정했다. 그러나 Task 5–6의 최신 보안 수정 `c5a596a`는 이제
독립 재검토에서 **BLOCK** 판정을 받았다. 이전 SHA `23b631f`의 raw error-body 누출은
후속 커밋에서 다뤄졌지만, 최신 리뷰는 provider-controlled error code가 예외 문자열로
반사될 수 있는 새 HIGH blocker를 확인했다. 따라서 Task 7은 이 blocker를 수정하고
최신 SHA를 재검토하기 전에는 시작하지 않는 것이 안전하다.

| 구간 | 상태 | 현재 근거/범위 |
|---|---|---|
| Task 1 | 완료 | Git/`uv` scaffold, Python 3.11 제약, offline CLI, `.env` ignore |
| Task 2 | 완료 | YAML+환경 overlay 설정, 명시 실행/요청/토큰 상한 검증, 재귀적 비밀값 마스킹 |
| Task 3 | 완료 | 보호 입력의 읽기 전용 SHA-256 inventory, 공식 문서 snapshot 모델 registry parser |
| Task 4 | 완료 | 불변 Pydantic schema, 결정적 ID, append-safe JSONL writer와 정규 export |
| Task 5 | 구현 완료·acceptance BLOCK | OpenAI-compatible·native v1/v3 adapter, budget/retry, SSE parser와 도착 시각 계측 |
| Task 6 | 구현 완료·acceptance BLOCK | 문서+live 모델 registry 병합, raw `/models` 처리, isolated capability-probe planning/execution |
| Task 7–15 | 미구현 | 아래 재개 순서 참고 |
| Task 16 | 미실행 live 단계 | 사용자 키 주입 및 작은 승인 범위가 선행 조건 |
| Task 17 | 미실행 승인 단계 | 원 계획에는 있으나, Task 16 성공·명시 범위/예산 승인 뒤에만 가능 |

## 3. 현재 아키텍처와 사용할 수 있는 표면

### 구현된 코드

- `src/hcx_eval/config.py`: `HarnessSettings`, `load_settings()`.
  `EXECUTE`가 참이면 API 키와 양수 `MAX_REQUESTS_PER_RUN`,
  `MAX_TOKENS_PER_RUN`을 요구한다.
- `src/hcx_eval/security.py`: mapping/free text/CLI 및 provider failure bytes의
  canonical secret redaction (`redact_bytes`) 경계.
- `src/hcx_eval/datasets/inventory.py`: 보호 입력을 변경하지 않는 결정적 inventory.
- `src/hcx_eval/discovery/docs_registry.py`: 공식 JSON snapshot을 파싱하고 문서
  근거·식별자·capability를 보존한다.
- `src/hcx_eval/schemas/`, `src/hcx_eval/artifacts/writer.py`, `src/hcx_eval/ids.py`:
  결과/manifest/model/case schema, 결정적 ID, append-safe artifact writer.
- `src/hcx_eval/clients/`: `RequestBudget`, `HttpExecutor`, OpenAI-compatible
  chat/embedding/`/models`, native v1/v3 chat, SSE parser. v1/v3 wire field와
  response contract는 분리되어 있다.
- `src/hcx_eval/registry/`: documented/live model merge,
  `discover_models()`, capability probe 계획과 결과 타입.

현재 `hcx-eval` CLI는 **명령 없이 실행할 때**
`Offline scaffold ready; no network action was performed.`만 출력한다. `--help`에는
현재 subcommand가 표시되지 않는다. 즉 원 계획에 있는 `inventory`, `discover`,
`build-cases`, `smoke`, `run`, `report` CLI는 아직 제공되지 않는다. Task 6의
`hcx-eval discover` 완료 기준도 아직 충족하지 않았다. 이 문서에서 “Task 6 구현 완료”는
library와 mocked test 범위라는 뜻이며, 원 계획의 전체 UX acceptance를 뜻하지 않는다.

구성 파일은 `configs/benchmark.default.yaml`, `models.seed.yaml`, `latency.yaml`,
`scoring.yaml`이고 기본값은 `execute: false`, 요청/토큰 상한 `0`이다.

## 4. 커밋 연대기

다음은 직접 `git log --reverse`로 확인한 주요 흐름이다.

| SHA | 제목 | 의미 |
|---|---|---|
| `5bf29e4` | `chore: initialize offline evaluation scaffold` | Task 1 baseline |
| `9cd4f96` | `feat: add offline safety and artifact foundations` | 설정·inventory·schema/artifact 기반 |
| `1031d7c` → `d402a69` | redaction/evidence hardening docs 및 fixes | Task 2–4의 redaction/immutability 보강 |
| `5d0a575` | `feat: add bounded CLOVA API adapters` | Task 5 adapter 첫 구현 |
| `d96dcf4` | `feat: add dynamic model registry discovery` | Task 6 registry/discovery 첫 구현 |
| `e91777e` | `fix: timestamp streaming events on arrival` | SSE 이벤트 수신 시각 보정 |
| `b310608` | `fix: enforce adapter wire contracts` | v1/v3·embedding wire contract 보강 |
| `bf852bc` | `fix: preserve model discovery provenance` | HCX-002/LK model provenance/status 보강 |
| `c5a596a` | `fix: redact provider failure evidence` | 이전 보안 BLOCK의 provider error/raw artifact 누출 경계 보강 |

### Task 5–6 리뷰 상태

기존 `.omo/evidence/tasks5-6-code-review.md`는 SHA `23b631f`에서 BLOCK을 냈다.
핵심 지적은 500 error body의 반사된 credential이 `ProviderApiError.response_body`와
discovery raw artifact에 남는다는 것이었다. `c5a596a`는 failure body와 malformed
success body를 `redact_bytes()`로 마스킹하고, 유효한 200 `/models` 바이트만 그대로
보존하도록 변경했다. 기존 `.omo/evidence/tasks5-6-security-fix/`는 해당 후속 커밋에서
100 tests, formatter/lint/type 통과와 synthetic failure probe를 **보고**한다.

최신 독립 재검토는 `.omo/evidence/tasks5-6-code-review.md`에 있고, SHA `c5a596a`에
대해 **BLOCK/REQUEST_CHANGES**를 기록한다. response body/discovery artifact의
sanitization은 통과했으나, `_error_details()`가 provider-controlled `status.code` 또는
`error.code`를 raw로 `ProviderApiError.provider_code`에 넣고 `__str__()`가 그것을 렌더링한다.
독립 MockTransport 재현에서 reflected credential marker가 예외 문자열에 남았다.
현재 test는 body/file만 확인하고 `provider_code`/`str(ProviderApiError)` 경계를 확인하지
않는다. 첫 수정은 provider code를 sanitize하거나 omit하고, 이 route를 잠그는 fake-wire
regression test를 추가하는 것이다. 수정 후 full gates와 해당 SHA의 독립 재검토를 다시
실행하기 전에는 `PASS`로 승격하지 않는다.

## 5. 직접 검증한 현재 증거

아래 명령은 기준 SHA `c5a596a`의 dirty product-code diff 없이 실행했다. 이 섹션 자체가
이번 handoff의 캡처 artifact이며, 각 성공 기준에 scenario·invocation·binary observable을
남긴다.

| Scenario | Invocation | Binary observable | Captured artifact |
|---|---|---|---|
| 전체 테스트 | `uv run pytest -q` | exit 0, `100 passed in 1.60s` | 이 문서 §5 |
| 형식·lint·type | `uv run ruff format --check . && uv run ruff check . && uv run basedpyright` | exit 0, `220 files already formatted`, `All checks passed!`, `0 errors, 0 warnings, 0 notes` | 이 문서 §5 |
| offline CLI | `uv run hcx-eval --help && uv run hcx-eval` | exit 0; help에 options만, 실행 출력은 고정 offline status | 이 문서 §5 |
| 보호 data inventory | `uv run python`으로 `build_inventory(Path("processed-data"))` | 208 files, 28,368,002 bytes, manifest SHA-256 `869e3c3db5c8a2f46b377b0739af2adb14ef4e0e22f01b59ab0828aea7253fb6` | 이 문서 §5 |
| 보호 docs inventory | 같은 inventory 명령 | 2 files, 468,392 bytes, manifest SHA-256 `33efc2ad7f87187b3b667542da874eb4cea88e59d0e2b3c9158837460c48b9a2` | 이 문서 §5 |
| 보호 tree/snapshot digest | sorted `sha256sum` tree 및 official JSON `sha256sum` | data tree `e1540402ae113ea08b8df310b797b34c070499759f11d788abc3da01098b80d3`; official JSON `f248d6c5a0034b82b5b4144fb0e32119d8f311e4e5c01241d3e66d02bf81b6bb` | 이 문서 §5 |
| Git patch hygiene | `git diff --check HEAD` 및 `git diff --check d402a69..HEAD` | 둘 다 exit 0/출력 없음 | 이 문서 §5 |

보호 입력은 Git에서 **untracked**다. 따라서 위 digest는 현재 바이트가 과거 evidence의
값과 일치한다는 강한 현재 비교일 뿐, Git history가 pre-task 원본 상태를 증명하는 것은
아니다. 이 caveat를 live run 전후 검증에도 유지한다.

### 실제 CLOVA 호출 여부

실제 CLOVA API request artifact, live `/models` snapshot, `.env`는 발견하지 못했다.
직접 실행한 CLI도 위의 고정 offline status만 출력했다. 기존 Task 5–6 evidence는 모든
HTTP probe가 `httpx2.MockTransport`와 `offline.invalid`를 사용했고
`external_clova_requests=0`이라고 **보고**한다. 따라서 이 handoff 시점의 정직한
결론은 **실제 CLOVA 호출 0건으로 취급하며, live 액세스는 아직 검증되지 않았다**이다.

## 6. 잔여 위험과 차단 조건

- 최신 `c5a596a`는 독립 review에서 HIGH BLOCK이다. provider-controlled error code가
  `ProviderApiError.provider_code`와 `str(ProviderApiError)`를 통해 reflected secret을
  누출할 수 있다. body/artifact sanitization은 통과했지만 이 예외 경계를 먼저 고친다.
- 현재 CLI는 live 계획을 노출/실행하지 않는다. Task 7–15에서 CLI 기능을 단계적으로
  추가하기 전에는 Task 16을 실행할 표면이 없다.
- redaction은 의미 있는 key/header/bearer 형태를 마스킹한다. marker 없는 임의 비밀
  문자열을 일반적으로 식별할 수 없으며, 유효한 `/models` 성공 response는 provenance
  계약상 byte-exact로 저장된다. 성공 response에 민감 값이 있다는 보장은 없다.
- live endpoint, model availability, capability, 가격, quota, rate limit, 실제 latency는
  전부 미검증이며 추정하면 안 된다.
- 기본 config의 비용 상한은 0이고 가격 근거도 아직 없다. 가격을 지어내지 말고
  `unknown` 또는 요청/토큰 ceiling을 사용한다.
- source data/docs와 평가 문서가 untracked인 현재 repository 구조는 remote handoff 시
  특별한 주의가 필요하다. 보호 입력을 원격에 무단 추가하지 않는다.

## 7. 권장 재개 순서

1. **BLOCKER 수정**: `src/hcx_eval/clients/executor.py`의 provider code 경계에서
   provider-controlled `status.code`/`error.code`를 sanitize 또는 omit하고,
   `str(ProviderApiError)`와 `provider_code` 모두 reflected credential marker를 내보내지
   않는 offline fake-wire regression을 추가한다. body/artifact redaction은 회귀시키지 않는다.
2. 새 SHA 독립 재검토: 500 error code, error body, malformed 200, exact valid 200 `/models`를
   MockTransport로 재실행하고 provider-code/error/artifact/no-secret 속성을 확인한다.
3. Task 7: source CSV를 읽기 전용으로 deterministic JSONL case로 변환한다. stable ID,
   encoding/required columns/duplicate, FAQ source/document group split, unreviewed
   paraphrase 경계를 테스트한다.
4. Task 8: EM/macro-F1/fact recall, retrieval/citation, JSON schema/tool argument,
   safety, latency percentile/bootstrap CI를 deterministic test-first로 만든다.
5. Task 9와 10: resume 가능한 bounded smoke/baseline runner 뒤, monotonic TTFT/E2E/
   TPOT runner를 구현한다. 실패·timeout·warmup을 버리지 않는다.
6. Task 11–13: embedding/API-tool, capability-specific (Thinking/structured/function/
   vision 분리), synthetic financial red-team을 차례로 추가한다.
7. Task 14–15: 두 종류의 보고서와 runbook/offline end-to-end를 완성한다. 원 계획의
   모든 CLI 명령을 dry-run preflight와 함께 제공한다.
8. 그 뒤에만 Task 16: 사용자가 키를 직접 주입하고 작은 scope를 승인한 뒤 live discovery
   와 smoke를 수행한다. Task 17 전체 benchmark는 별도 승인이다.

## 8. bootstrap, 환경변수 이름, 검증 명령

```bash
uv sync
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
uv run hcx-eval --help
uv run hcx-eval
```

`.env.example`에 있는 이름만 사용한다. 값·header·key는 이 문서나 terminal 기록에
인쇄하지 않는다.

```text
CLOVA_STUDIO_API_KEY
CLOVA_STUDIO_BASE_URL
CLOVA_OPENAI_BASE_URL
DATA_ROOT
NAVER_DOCS_ROOT
RESULTS_ROOT
REQUEST_TIMEOUT_SECONDS
MAX_CONCURRENCY
MAX_REQUESTS_PER_RUN
MAX_TOKENS_PER_RUN
MAX_ESTIMATED_COST_KRW
EXECUTE
```

Task 16 직전에는 source hash를 다시 기록하고, configuration validation과 새 CLI의
`discover --dry-run`을 먼저 실행해야 한다. 이후 승인된 작은 smoke의 **예상 요청**은
다음과 같다(현재 실제 CLI는 미구현이므로 실행 지시가 아니라 acceptance 목표다).

- 1회 OpenAI-compatible `GET /models` snapshot.
- live generation model마다 최소 text request 1회.
- live embedding model마다 최소 embedding request 1회.
- live와 documented capability가 교집합인 model/capability별 최소 isolated probe 1회.
- 모든 요청에는 run ID, model, API family, ceiling, sanitized failure/success artifact
  경로를 남긴다. request budget보다 많아지면 즉시 중단한다.

원 계획의 예시 CLI는 구현 후 다음 순서로 검증한다.

```bash
uv run hcx-eval inventory
uv run hcx-eval discover --dry-run
uv run hcx-eval discover
uv run hcx-eval smoke --max-requests 20
uv run hcx-eval build-cases --dataset structured
uv run hcx-eval run --phase faq --models all --max-requests 100
uv run hcx-eval report --run-id <RUN_ID>
```

`discover`, `smoke`, `run`, `report`는 현재 존재하지 않는다. 구현되는 각 단계에서
mocked integration evidence를 먼저 남기고, live 명령은 사용자 승인 후에만 실행한다.

## 9. Git/remote 핸드오프

- 현재 branch는 `main`, `HEAD`는 `c5a596a`에서 이 handoff commit으로 전진한다.
- upstream과 remote는 설정되지 않았다(`git remote -v` 출력 없음,
  `git rev-parse --abbrev-ref @{upstream}`은 no upstream 오류). push 여부도 알 수 없다.
- `docs/model-evaluation/`, `processed-data/`,
  `naver-clova-studio-instructions-all-docs/`, 기존 `.hermes/`, `.codegraph/`는
  untracked 사용자 입력/작업으로 남아 있다. 이 handoff commit에는 새 handoff 문서와
  최소 `.omo` 상태 정정만 stage한다.
- remote를 연결하기 전에는 `.env`가 ignored인지 재확인하고, 보호 input/raw results를
  무단으로 stage/push하지 않는다. 새 remote/공개/대량 결과 commit은 사용자 승인이
  필요한 별도 작업이다.

## 10. 상태 파일 정정

`.omo/plans/hyperclova-offline-harness.md`와
`.omo/ledgers/hyperclova-offline-harness.json`은 이 handoff와 함께 Task 5–6을
구현 완료로 정정한다. 단, latest independent review는 `c5a596a`에서 `BLOCK`이며,
다음 구현 작업은 Task 7이 아니라 provider-code secret-reflection fix다. 이 정정은 live
실행 승인이나 품질 gate PASS를 의미하지 않는다.

## 11. 이 핸드오프의 자체 검증

commit 전 수행할 scenario는 다음이다.

| Scenario | Invocation | Binary observable | Captured artifact |
|---|---|---|---|
| Markdown sanity | heading/list/code-fence balance 검사 | exit 0, unclosed fence 0 | 이 문서 §11 검증 로그 |
| Secret scan | canonical secret assignment/header pattern으로 새 문서와 staged diff 검사 | exit 0, prohibited value-like match 0 | 이 문서 §11 검증 로그 |
| Commit scope | `git diff --cached --name-only`와 staged diff review | 새 handoff와 두 최소 상태 파일만 staged | 이 문서 §11 검증 로그 |

직접 검증 결과(커밋 직전): Markdown sanity는 `PASS`, 275 lines, fenced marker 6개(짝수)였고
unclosed fence는 0개였다. 값이 있는 canonical credential assignment/bearer pattern secret
scan은 0건이어야 하며, staged scope는 이 handoff와 `.omo`의 두 상태 파일, 총 3개 파일이다.
이 문서가 그 검증의 영구 캡처 artifact다.
