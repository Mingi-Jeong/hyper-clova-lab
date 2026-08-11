# HyperCLOVA 구현 핸드오프 직접 검증

검증 기준 커밋: `cd1ed8d29fb7f07f06abaad7dc6859389c4e673c`
검증 시각: 2026-08-12 (Asia/Shanghai)

이 파일은 stop-hook 요구에 따라 기존 보고를 신뢰하지 않고, 현재 workspace에서 직접
실행한 출력과 판단을 기록한다. 비밀값, 헤더 값, `.env` 내용은 수집하지 않았다.

| 성공 기준/시나리오 | 실제 invocation | binary observable | 직접 관찰한 결과 | 판단 |
|---|---|---|---|---|
| Python 전체 회귀 | `uv run pytest -q` | exit 0 및 모든 test 통과 | `100 passed in 1.67s` | PASS |
| 형식·lint·type | `uv run ruff format --check . && uv run ruff check . && uv run basedpyright` | exit 0 | `221 files already formatted`; `All checks passed!`; `0 errors, 0 warnings, 0 notes` | PASS |
| 실제 사용자 offline CLI surface | `uv run hcx-eval --help && uv run hcx-eval` | exit 0, 네트워크 대신 offline status | help에는 option만 있고 `Offline scaffold ready; no network action was performed.` 출력 | PASS: 현재 구현된 offline surface |
| 보호 data read-only identity | `build_inventory(Path("processed-data"))`; sorted `sha256sum` tree | 기대 manifest/tree digest 일치 | 208 files, 28,368,002 bytes, manifest `869e3c3db5c8a2f46b377b0739af2adb14ef4e0e22f01b59ab0828aea7253fb6`; tree `e1540402ae113ea08b8df310b797b34c070499759f11d788abc3da01098b80d3` | PASS: 현재 바이트가 기존 기준과 일치 |
| 보호 official docs identity | `build_inventory(Path("naver-clova-studio-instructions-all-docs"))`; JSON `sha256sum` | 기대 manifest/file digest 일치 | 2 files, 468,392 bytes, manifest `33efc2ad7f87187b3b667542da874eb4cea88e59d0e2b3c9158837460c48b9a2`; JSON `f248d6c5a0034b82b5b4144fb0e32119d8f311e4e5c01241d3e66d02bf81b6bb` | PASS: 현재 바이트가 기존 기준과 일치 |
| handoff Markdown·상태 JSON | `uv run python -m json.tool ...`; fence/trailing-whitespace/credential-value scanner | exit 0, balanced fence, no value-like credential match | `markdown_sanity=PASS lines=275 fenced_markers=6`; `secret_value_pattern_matches=0` | PASS |
| handoff commit scope·whitespace | `git show --check --format=oneline HEAD`; `git diff-tree --no-commit-id --name-status -r HEAD` | no whitespace error; exactly three intended paths | `A .hermes/plans/2026-08-12_hyperclova-offline-implementation-handoff.md`; `M .omo/ledgers/hyperclova-offline-harness.json`; `M .omo/plans/hyperclova-offline-harness.md` | PASS |

## 판단 경계

- 보호 입력은 Git에서 untracked다. 위 hash는 현재 바이트가 기록된 기준과 일치한다는
  검증이지, Git history가 pre-task 원본을 증명하는 것은 아니다.
- 실제 CLOVA 호출은 이 검증에서 수행하지 않았다. CLI의 직접 관찰 결과는 offline
  status뿐이다. live discovery/smoke는 사용자 키와 명시 승인 및 선행 CLI 구현 뒤에만
  수행할 수 있다.
- Task 5–6은 구현 범위로는 기록되었지만 acceptance PASS가 아니다. 독립 review
  `.omo/evidence/tasks5-6-code-review.md`는 `c5a596a`에서 provider-controlled error
  code가 exception text에 반사될 수 있다는 HIGH BLOCK을 기록한다. 이 증거는 그
  blocker를 해결하지 않으며, handoff가 그 blocker를 첫 후속 작업으로 정확히 기록했음을
  확인할 뿐이다.
