# 06. CLOVA Studio 전체 모델·API 테스트 범위

## 1. 근거 snapshot

평가의 플랫폼 근거는 다음 read-only 수집본입니다.

```text
naver-clova-studio-instructions-all-docs/
├── naver_clova_studio_all_docs.md
└── naver_clova_studio_all_docs.json
```

- 수집 시각: 2026-08-12T03:33:58+09:00
- 공식 API 가이드 문서: 31개
- 섹션: 11개
- Markdown: 6,227줄, 220,354 bytes
- JSON: 248,038 bytes

원본 수집본은 수정하지 않습니다. 실험 manifest에는 두 파일의 SHA-256과 수집 시각을 기록합니다.

## 2. “전체 테스트”의 정의

전체 테스트는 문서에 이름이 보이는 모델만 하드코딩하는 것이 아닙니다.

1. OpenAI-compatible `GET /models` 결과 전부 수집
2. native v1/v3 문서 발견 모델을 registry와 대조
3. 각 모델을 `live`, `restricted`, `deprecated`, `unavailable`, `historical-example-only`로 판정
4. live 모델은 공통 baseline 전수 실행
5. capability가 있는 모델은 기능별 트랙 추가 실행
6. 호출 불가 모델도 오류 코드와 근거를 보존
7. 모델 외 임베딩·RAG·리랭커·라우터 API도 별도 scorecard로 평가

## 3. 최소 registry

| 분류 | 발견 대상 |
|---|---|
| v3 생성 | HCX-007, HCX-005, HCX-DASH-002 |
| classic/legacy 생성 | HCX-003, HCX-DASH-001 |
| historical example | HCX-002 |
| 임베딩 | bge-m3, clir-emb-dolphin, clir-sts-dolphin |
| 교체 이력 | LK-B, LK-D2 |
| 동적 발견 | `/models`가 반환하는 위 목록 외 모든 ID |

## 4. 공통 baseline과 capability별 트랙

모든 live 생성 모델:

- short-context 금융 FAQ·코드·안전성·한국어 평가
- streaming/non-streaming 응답시간
- 오류·timeout·429·5xx
- 같은 입력/목표 출력 길이 기준의 공정 비교

지원 모델만 추가:

- Thinking: effort별 정확도-지연-토큰 곡선
- Vision: 표·이미지·스캔 문서 QA
- Structured Outputs: JSON Schema validation
- Function calling: tool/argument/결과 반영
- Long context: 8k/32k/100k 및 한도 근처
- Tuning: 별도 비용·side effect 승인 후 수행

## 5. 응답시간을 주요 의사결정 변수로 처리

모델 순위는 평균 응답시간 하나로 정하지 않습니다.

- 사용자가 기다리기 시작하는 시간: TTFT
- 답변이 끝나는 시간: E2E
- 생성 체감 속도: TPOT, token/s, inter-token gap
- 나쁜 날의 경험: p95/p99, max stall
- 부하 내성: concurrency별 latency와 429/timeout
- 파이프라인 비용: retrieval/reranker/LLM/guard 각각의 구간 지연

최종 보고서는 품질-지연-비용 Pareto frontier를 제시하며, 업무별 SLO를 만족하지 못한 모델은 높은 평균 품질만으로 채택하지 않습니다.

## 6. 장단점 보고 규칙

각 모델·API마다 반드시 다음을 작성합니다.

1. 가장 잘한 업무와 효과 크기
2. 가장 취약한 업무와 재현 가능한 실패 사례
3. 기능 지원/미지원과 context/output 한도
4. TTFT/E2E/tail latency와 부하 민감도
5. 안정성 gate 결과
6. 비용 및 cost per correct answer
7. 권장 역할, 금지 역할, 필요한 Guard/RAG 조건

단일 “최고 모델” 결론보다 FAQ·비전·복합 추론·분류·검색 등 업무별 최적 조합과 routing 정책을 우선 도출합니다.
