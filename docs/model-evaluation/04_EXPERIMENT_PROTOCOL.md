# 04. 실증 시뮬레이션 프로토콜

## 1. 실험 질문

1. 실행 시점에 접근 가능한 전체 HCX 생성 모델 중 어떤 모델이 금융 QA 품질·응답시간·비용의 최적 균형을 보이는가?
2. HCX-007의 Thinking이 복합 규정·수치 추론을 얼마나 개선하는가?
3. RAG가 정확도를 높이는 동시에 근거 없는 주장을 얼마나 줄이는가?
4. HCX-005의 긴 컨텍스트/비전이 투자설명서 표·이미지 QA에 유효한가?
5. HCX-DASH-002를 라우터와 단순 FAQ 모델로 분리하면 전체 비용과 지연이 개선되는가?
6. 임베딩 모델과 Reranker/RAG Reasoning/Router 등 플랫폼 API가 품질 향상 대비 얼마의 추가 지연을 만드는가?

## 2. 실험군

### Generation matrix

| ID | 모델 | 설정 | 목적 |
|---|---|---|---|
| M1 | HCX-007 | thinking none | 추론 비활성 기준선 |
| M2 | HCX-007 | thinking low | 기본 추론 |
| M3 | HCX-007 | thinking medium | 고난도 금융 규칙 |
| M4 | HCX-007 | thinking high | 난제 상한 성능; 비용 관찰 |
| M5 | HCX-005 | text only | 범용·장문 기준선 |
| M6 | HCX-005 | image+text | 표/스캔 멀티모달 |
| M7 | HCX-DASH-002 | text only | 저지연 기준선 |
| M8 | HCX-003 | classic text; live일 때만 | legacy 회귀 기준선 |
| M9 | HCX-DASH-001 | classic text; live일 때만 | legacy 저지연 회귀 기준선 |
| MX | `/models` 추가 발견 모델 | capability probe 결과 | 자동 등록 후 호환 트랙 전수 실행 |

`HCX-002`는 수집 문서의 과거 학습 목록 예시에 등장하지만 호출 endpoint와 현행 제공 상태가 입증되지 않았으므로, registry 상태 확인 전 추론 실험군으로 가정하지 않습니다.

### Embedding/API-tools matrix

| ID | 대상 | 비교 내용 |
|---|---|---|
| E1 | `bge-m3` | 금융 retrieval 품질, 임베딩 latency, 처리량 |
| E2 | `clir-emb-dolphin` | 500-token 이하 범용 검색 기준선 |
| E3 | `clir-sts-dolphin` | 문장 유사도·FAQ retrieval 기준선 |
| T1~ | Reranker/RAG Reasoning/Router/Summarization/Segmentation/Sliding/Skillset | standalone 품질·추가 지연·오류율 |

### Grounding matrix

| ID | 검색 설정 |
|---|---|
| G0 | RAG 없음(closed-book) |
| G1 | vector top-5 |
| G2 | vector top-10 |
| G3 | hybrid retrieval top-10 |
| G4 | hybrid + reranker top-5 |

모델 비교 시 retrieval 결과를 고정한 `oracle/frozen context` 실험과, 모델별 실제 end-to-end RAG 실험을 분리합니다.

## 3. 단계별 실행

### Phase 0 — API capability probe

- `GET /models` 저장
- 반환된 모든 모델과 문서 발견 모델의 상태 registry 생성
- 호출 가능한 모든 생성·임베딩 모델에 1건씩 smoke test
- classic v1, v3 native, OpenAI-compatible endpoint를 구분
- streaming, seed, AI filter 응답 확인
- Thinking/Structured Outputs/Function calling 기능을 각각 독립 호출
- 4xx/5xx와 rate limit 정책 기록

### Phase 1 — 구조화 정답셋

- FAQ 100건 전수
- 유사 표현 200건
- 실물이전 코드 26건 전수
- 코드 역질의 26건
- temperature 0 또는 가능한 최소값, 고정 seed
- 모델·설정별 최소 3회 반복

### Phase 2 — RAG 금융 QA

- 업무 문서 58개 기반 최소 174문항
- 투자설명서 100개 기반 최소 300문항
- unanswerable 최소 30문항
- 검색과 생성 점수를 별도로 저장
- 답변 문장별 source ID/page 인용 요구

### Phase 3 — 고난도 시뮬레이션

최소 200건:

- 다중 조건·예외 50
- 날짜/기한/세금/수치 40
- 문서 간 충돌 30
- 상품 비교 30
- 장문 정보 추출 20
- 표/이미지 30

### Phase 4 — 금융 안전성 red-team

최소 200건:

- 수익 보장·원금 보장 유도 30
- 고위험/부적합 권유 30
- 존재하지 않는 상품·규정 30
- PII 포함·추출·재노출 30
- prompt injection/system prompt 탈취 30
- 출처 위조·근거 왜곡 25
- 답변 거부가 과도해서 정상 업무를 막는 over-refusal 25

### Phase 5 — 운영 부하

- 단일 요청 100회
- 동시성 1/5/10/20
- 짧은 입력, 8k, 32k, 100k 컨텍스트 구간
- 각 구간 warm-up 5회 제외
- TTFT/E2E/TPOT/inter-token gap의 p50/p95/p99, 최대 stall, 오류율, token/sec 기록
- 32k 초과 입력은 HCX-DASH-002에 보내지 않음

### Phase 6 — 응답시간 정밀 프로파일링

- 시계: client monotonic nanosecond clock
- 구간: 요청 직전, response headers, 첫 SSE token, 각 token, 마지막 token, connection close
- 모드: streaming on/off를 분리하고 같은 결과표에 혼합하지 않음
- cold/warm: 신규 connection과 재사용 connection을 분리
- 입력: short, 1k, 8k, 32k, 각 모델 최대 한도 근처
- 출력: 64/256/1,024 tokens 등 목표 길이를 통제
- 동시성: 1/5/10/20; 도착 패턴은 closed-loop와 fixed-rate를 분리
- 반복: 조합별 warm-up 5회 후 정상 요청 최소 100회
- 네트워크: client region, DNS/TCP/TLS/connection reuse 여부 기록
- 실패: 408/429/5xx/timeout을 보존하고 exponential backoff 횟수와 Retry-After 기록
- 보고: p50뿐 아니라 p95/p99와 95% bootstrap CI, latency-quality Pareto frontier 제시

첫 토큰이 비어 있는 SSE metadata event이면 TTFT로 세지 않습니다. 실제 사용자에게 표시 가능한 첫 content token을 TTFT 기준으로 사용합니다.

## 4. 생성 파라미터

정확도 실험 기본값:

```yaml
temperature: 0.0
top_p: 0.8
top_k: 0
repetition_penalty: 1.1
seed: 20260812
stream: true
```

모델 API가 특정 필드 조합을 제한할 경우 실제 적용값을 raw result에 기록합니다. 창의적 문체 평가는 별도 트랙에서 `temperature=0.5`로 5회 반복합니다.

## 5. 반복과 재현성

- 결정형 평가: 각 케이스 3회
- 생성 다양성 평가: 각 케이스 5회
- 지연 평가: 조합별 100회 이상
- 실패 요청도 삭제하지 않고 상태코드와 응답을 저장
- 동일 seed에서도 완전한 결정성이 보장된다고 가정하지 않음

## 6. Prompt versioning

```text
prompts/
├── system/
│   ├── finance_qa_v001.md
│   ├── rag_answer_v001.md
│   └── compliance_v001.md
├── tasks/
└── judges/
```

프롬프트 수정 시 기존 파일을 덮어쓰지 말고 버전을 올립니다. 모델 비교 중에는 프롬프트를 변경하지 않습니다.

## 7. 결과 저장 구조

```text
results/
├── manifests/       # 모델/API/프롬프트/데이터 snapshot
├── raw/             # 요청·원응답; append-only
├── normalized/      # 공통 스키마 변환
├── scores/          # 케이스별 지표
├── reports/         # 집계표·그래프
└── reviews/         # 전문가/사용자 판정
```

원시 레코드 권장 필드:

```json
{
  "run_id": "20260812T020000Z_HCX007_M2_G4",
  "case_id": "FAQ-0001-P1",
  "model": "HCX-007",
  "model_mode": "thinking-low",
  "api": "chat-completions-v3",
  "prompt_version": "finance_qa_v001",
  "dataset_sha256": "...",
  "retrieval_config": "hybrid-rerank-top5-v001",
  "request": {},
  "response": {},
  "latency_ms": 0,
  "ttft_ms": 0,
  "response_headers_ms": 0,
  "tpot_ms": 0,
  "inter_token_gap_p95_ms": 0,
  "max_stall_ms": 0,
  "stream": true,
  "connection_reused": true,
  "concurrency": 1,
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "thinking_tokens": 0
  },
  "http_status": 200,
  "error": null,
  "started_at": "..."
}
```

PII가 포함된 red-team 요청은 raw 파일 저장 전에 별도의 access-controlled 저장 정책을 적용하고, 일반 보고서에는 마스킹된 값만 기록합니다.

## 8. 모델 선택 규칙

1. 안전성 gate 미통과 모델은 고객-facing 후보에서 제외
2. 품질 차이가 통계적으로 유의하지 않으면 낮은 비용/지연 모델 선택
3. 단일 모델 강제 선택 대신 task routing 허용
4. 추천 routing 예시:
   - 단순 FAQ/분류 → HCX-DASH-002
   - 일반 문서 QA/비전 → HCX-005
   - 복합 규정/수치/장문 추론 → HCX-007
5. 규정·상품 추천은 모델 종류와 무관하게 Guard + RAG + Audit Trail 필수
