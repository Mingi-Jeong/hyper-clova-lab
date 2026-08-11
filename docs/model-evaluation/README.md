# HyperCLOVA X 금융 모델 평가 문서

> 기준 시점: 2026-08-12 (CST)  
> 프로젝트: `/home/workspace/hyper-clova-lab`  
> 평가 데이터: `/home/workspace/hyper-clova-lab/processed-data`  
> 플랫폼 문서 snapshot: `/home/workspace/hyper-clova-lab/naver-clova-studio-instructions-all-docs`

## 목적

이 폴더는 HyperCLOVA X 모델을 금융·연금·펀드 업무에 적용하기 전에, 모델의 **정확성·근거성·추론력·한국어 품질·컴플라이언스·구조화 출력·운영 효율성**을 재현 가능한 방식으로 평가하기 위한 기준 문서입니다.

평가는 단순 질의응답 정확도만 보지 않습니다. 다음 4개 계층을 모두 측정합니다.

1. **Model layer**: 지식, 추론, 지시 준수, 한국어 생성
2. **Grounding layer**: 검색, 인용, 문서 근거 충실도, 장문 처리
3. **Guard layer**: 개인정보, 투자 권유, 과장 표현, 프롬프트 공격
4. **Operations layer**: 지연시간, 실패율, 토큰, 비용, 재현성

## 문서 구성

| 문서 | 역할 |
|---|---|
| [01_DATASET_INVENTORY.md](01_DATASET_INVENTORY.md) | 현재 데이터셋의 수량·구조·평가 활용법 |
| [02_HYPERCLOVA_MODEL_CATALOG.md](02_HYPERCLOVA_MODEL_CATALOG.md) | 현재 확인된 NAVER 모델과 API 기능 비교 |
| [03_EVALUATION_METHODOLOGY.md](03_EVALUATION_METHODOLOGY.md) | 다층 평가 항목, 지표, 가중치, 합격 기준 |
| [04_EXPERIMENT_PROTOCOL.md](04_EXPERIMENT_PROTOCOL.md) | 실험군, 반복 횟수, 통계, 결과 저장 규칙 |
| [05_SCORECARD_TEMPLATE.md](05_SCORECARD_TEMPLATE.md) | 모델별 정량 결과표와 의사결정 템플릿 |
| [06_FULL_PLATFORM_TEST_SCOPE.md](06_FULL_PLATFORM_TEST_SCOPE.md) | 전체 모델·임베딩·API 도구의 발견, 상태 판정, 전수 테스트 범위 |

## 현재 데이터 요약

- 평가용 Markdown: **158개** (`docs` 58개 + `투자설명서` 100개)
- Markdown 총량: 약 **24.2MB**
- 구조화 정답셋: **135건**
  - 디폴트옵션 FAQ 100건
  - 디폴트옵션 출처 9건
  - 실물이전 불가 사유 26건
- 원문 문서 페이지 마커: README 기준 **6,625쪽**
- 이미지·미디어: 멀티모달 평가에서만 선택적으로 사용

## 전체 평가 대상 원칙

평가 대상을 특정 3개 생성 모델로 고정하지 않습니다. 실행 시점의 `GET /v1/openai/models`와 native API capability probe에서 발견되는 **모든 호출 가능 모델**을 자동 등록하고 smoke test 후 전체 또는 호환 가능한 평가 트랙에 배치합니다.

수집 문서에서 확인된 모델 식별자는 다음과 같습니다.

- 현행 v3 생성·추론: `HCX-007`, `HCX-005`, `HCX-DASH-002`
- classic/legacy 생성·튜닝 문서: `HCX-003`, `HCX-DASH-001`, 예시 이력의 `HCX-002`
- 임베딩: `bge-m3`, `clir-emb-dolphin`, `clir-sts-dolphin`

문서에 등장했다고 현재 호출 가능하다고 가정하지 않습니다. `available`, `restricted`, `deprecated`, `unavailable`, `historical-example-only` 상태를 실제 API 결과와 함께 기록합니다. 호출 불가능한 모델도 목록에서 삭제하지 않고 HTTP 상태·오류 코드·판정 근거를 보존합니다.

## 핵심 원칙

- 같은 프롬프트, 같은 검색 결과, 같은 생성 파라미터로 모델을 비교합니다.
- 모델 지식 평가와 RAG 평가를 분리합니다.
- 정답 정확도와 근거 충실도를 분리합니다.
- 평균 점수만으로 통과시키지 않고 금융 안전성에 **하드 게이트**를 둡니다.
- 실험 결과 원본은 삭제하지 않고 `results/raw/`에 누적합니다.
- 모델명, API 버전, 프롬프트 버전, 데이터 해시, 실행 시각을 반드시 기록합니다.
- 평균 지연만 보고하지 않고 **TTFT·E2E·TPOT·token/s·inter-token gap·p50/p95/p99·오류/timeout 비율**을 함께 기록합니다.
- 생성 모델, 임베딩 모델, RAG/리랭커/라우터 등 플랫폼 API 도구는 서로 다른 평가 트랙과 scorecard를 사용합니다.

## 권장 다음 단계

1. `default_option_faq_100.csv`와 `in_kind_transfer_restriction_reasons.csv`를 자동평가 JSONL로 변환
2. 58개 업무 문서와 100개 투자설명서에서 근거 포함 QA 세트 구축
3. `/models`와 native endpoint probe로 전체 모델 snapshot 생성
4. RAG 미사용/사용, 모델별, 프롬프트별 ablation 비교
5. 전문가 검토 표본을 별도로 운영하여 자동평가 편향 점검
