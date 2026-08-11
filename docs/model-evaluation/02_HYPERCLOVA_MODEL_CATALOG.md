# 02. NAVER HyperCLOVA X 모델 카탈로그

> 조사 기준: 2026-08-12  
> 모델 제공 상태와 한도는 변경될 수 있으므로 실험 시작 시 `/models` API와 공식 문서를 다시 확인합니다.

## 1. 수집 자료와 평가 범위

사용자 수집 snapshot은 2026-08-12 기준 공식 API 가이드 **31개 문서, 11개 섹션**을 포함합니다. 이 snapshot에서 발견한 모델 식별자를 전부 관리하되, 문서 등장과 현재 서비스 가능 여부를 구분합니다.

## 2. 생성 모델 전체 발견 목록

| 모델 | 문서상 계열/상태 | 입력/출력 한도 | 핵심 기능 | 평가 처리 |
|---|---|---|---|---|
| `HCX-007` | 현행 v3 추론형 | 합계 128K / 출력 최대 32,768 | Thinking, Structured Outputs | 모든 text·reasoning·latency 트랙 |
| `HCX-005` | 현행 v3 범용·비전 | 합계 128K / 출력 최대 4,096 | text, vision, Function calling | text·vision·tool·latency 트랙 |
| `HCX-DASH-002` | 현행 v3 경량형 | 합계 32K / 출력 최대 4,096 | text, streaming | text·batch·latency 트랙 |
| `HCX-003` | classic v1 및 튜닝 문서 | 합계 8,192 / 입력 최대 7,600 / 출력 최대 4,096 | classic chat, tuning 관련 | live probe 후 legacy 회귀·지연 비교 |
| `HCX-DASH-001` | classic v1 문서 | 합계 4,096 / 입력 최대 3,500 / 출력 최대 4,096 | classic lightweight chat | live probe 후 legacy 회귀·지연 비교 |
| `HCX-002` | 학습 목록 응답 예시의 과거 식별자 | snapshot만으로 한도 확정 불가 | 과거 task record 예시 | historical 여부 확인; 임의 호출 금지 |

`GET /models`에서 이 표에 없는 모델이 발견되면 즉시 manifest에 추가하고 capability probe를 실행합니다. 즉, 이 표는 allowlist가 아니라 **최소 발견 목록**입니다.

### HCX-007

- 복잡한 문제 해결을 위한 추론 모델
- `thinking.effort`: `none`, `low`, `medium`, `high`
- 기본 최대 생성 토큰:
  - none: 512
  - low: 5,120
  - medium: 10,240
  - high: 20,480
- 설정 가능 최대 출력: 32,768
- 입력+출력 합계: 128,000 이하
- 이미지와 튜닝 학습 미지원
- Thinking, Function calling, Structured Outputs를 동시에 사용할 수 없음
- `thinkingContent`와 추론 토큰 사용량을 응답에서 확인 가능

### HCX-005

- 텍스트와 이미지 이해가 가능한 비전 모델
- 입력 토큰 최대 128,000, 입력+출력 합계 128,000 이하
- 출력 최대 4,096
- 이미지: 턴당 1개, 요청당 최대 5개
- 이미지 형식: BMP, PNG, JPG/JPEG, WEBP
- 이미지 크기: 20MB 이하, 긴 변 2,240px 이하
- 이미지 입력을 사용하는 작업은 튜닝 미지원

### HCX-DASH-002

- 경량화된 저지연 모델
- 입력 토큰 최대 32,000, 입력+출력 합계 32,000 이하
- 출력 최대 4,096
- 이미지 미지원
- FAQ·분류·요약·라우팅에서 성능/비용 효율 기준선으로 사용

## 3. 임베딩 모델 전체 발견 목록

| 모델 | 유형 | 비고 |
|---|---|---|
| `bge-m3` | 임베딩 v2/OpenAI 호환 | OpenAI 호환 예제의 지원 모델명; 생성 모델 아님 |
| `clir-emb-dolphin` | 임베딩 v1 | 범용 임베딩, 입력 1~500 tokens |
| `clir-sts-dolphin` | 임베딩 v1 | 문장 의미 유사도 특화, 입력 1~500 tokens |

RAG 평가는 생성 모델과 검색 모델을 분리해야 합니다. 예를 들어 `bge-m3 + HCX-007`의 결과가 좋더라도 이를 HCX-007 단독 지식 성능으로 해석하면 안 됩니다.

## 4. 모델 외 플랫폼 API 전수 평가

다음 API는 생성 모델과 동일 총점으로 섞지 않고 별도 트랙에서 품질·응답시간·오류율을 측정합니다.

| API/기능 | 핵심 평가 |
|---|---|
| Reranker | nDCG/MRR 향상, p50/p95/p99 추가 지연 |
| RAG Reasoning | 정답성, citation fidelity, TTFT/E2E |
| Router | intent macro-F1, confidence calibration, latency |
| Summarization | 사실 보존, 압축률, latency/input length curve |
| Segmentation | 경계 F1, downstream retrieval gain, latency |
| Sliding Window | 정보 보존율, 탈락 위치, 처리시간 |
| Tokenizers | 실제 usage와 차이, 처리량 |
| Skillset final answer | tool 결과 반영, 오류 복구, end-to-end latency |
| Tuning APIs | 지원 모델·상태·제약 확인; 별도 승인 없는 학습 job 생성 금지 |

## 5. API 기능

### Native API

```text
POST https://clovastudio.stream.ntruss.com/v3/chat-completions/{modelName}
```

### OpenAI 호환 API

```text
Base URL: https://clovastudio.stream.ntruss.com/v1/openai
POST /chat/completions
POST /embeddings
GET  /models
```

Python SDK 기본 형태:

```python
from openai import OpenAI

client = OpenAI(
    api_key="CLOVA_STUDIO_API_KEY",
    base_url="https://clovastudio.stream.ntruss.com/v1/openai",
)
```

## 6. 금융 실험 배치 원칙

1. 모든 live 생성 모델에 공통 분모인 short text QA·안전성·한국어·지연 baseline을 적용합니다.
2. 기능별 capability가 있는 모델만 vision, Thinking, Structured Outputs, Function calling 트랙에 배치합니다.
3. context 한도를 넘는 입력은 축약해 공정 비교하지 않고 `unsupported_by_limit`로 기록합니다.
4. classic/legacy 모델이 호출 가능하면 현행 모델과 동일 short-context frozen prompt로 회귀 비교합니다.
5. 모든 모델의 장점뿐 아니라 실패 유형, 기능 부재, 한도, tail latency, rate-limit 민감도를 함께 기록합니다.

## 7. 과거/교체 모델 관리

과거 모델은 임의로 제외하지 않습니다. 다만 현재 API가 노출하지 않거나 접근 권한이 없는 경우 실제 추론 비교가 불가능하므로, 상태 확인 결과를 `unavailable/deprecated/historical-example-only`로 남깁니다. `LK-B`, `LK-D2`처럼 교체 안내된 식별자도 같은 registry에 보존하되, 추측한 endpoint로 호출하지 않습니다.

모델 목록을 코드에 하드코딩하지 않고 실험 시작 전 아래 순서로 확정합니다.

1. OpenAI 호환 `GET /models` 응답 저장
2. 각 후보 모델에 1건 smoke test
3. 지원 기능(vision/thinking/structured/function calling) capability probe
4. `models_snapshot_YYYYMMDD.json`으로 결과 보존

## 8. 공식 출처

- Chat Completions V3 텍스트/이미지: https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3
- 추론(Thinking): https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3-thinking
- Function calling: https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3-fc
- Structured Outputs: https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3-so
- OpenAI 호환성: https://api.ncloud-docs.com/docs/clovastudio-openaicompatibility
- CLOVA Studio 릴리스 노트: https://api.ncloud-docs.com/docs/clovastudio-releasenote
- 전체 API 문서 인덱스: https://api.ncloud-docs.com/llms.txt

## 9. 조사 신뢰도 메모

- `api.ncloud-docs.com`의 Markdown/API 문서를 직접 확인했습니다.
- 사용 가이드 도메인 `guide.ncloud-docs.com`은 조사 환경에서 Cloudflare 403이 발생하여, API 문서와 네이버 검색 색인을 교차 확인했습니다.
- 가격은 계약·리전·정책에 따라 달라질 수 있어 본 문서에 추정값을 적지 않았습니다. 실제 청구 단가를 확보한 뒤 scorecard에 입력합니다.
- 사용자 수집 snapshot의 Markdown은 6,227줄/220,354 bytes, JSON은 31개 문서를 구조화해 보존합니다. 평가 근거는 이 snapshot의 문서 URL·수집시각·원문 hash와 연결합니다.
