# 05. HyperCLOVA X 모델 평가 Scorecard

## 1. 실행 정보

| 필드 | 값 |
|---|---|
| Run ID | |
| 실행일 | |
| 데이터 버전/SHA | |
| Prompt version | |
| Retrieval version | |
| API snapshot | |
| 평가자/Judge version | |
| 실제 가격표 기준일 | |

## 2. 모델별 종합 점수

| 모델/설정 | API/상태 | 금융 정확도 20 | RAG 15 | 추론 15 | 안전 20 | 지시 10 | 한국어 5 | 응답시간·운영 15 | 총점 | Gate | 등급 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| HCX-007 none | v3/live? | | | | | | | | | | |
| HCX-007 low | v3/live? | | | | | | | | | | |
| HCX-007 medium | v3/live? | | | | | | | | | | |
| HCX-007 high | v3/live? | | | | | | | | | | |
| HCX-005 text | v3/live? | | | | | | | | | | |
| HCX-005 vision | v3/live? | | | | | | | | | | |
| HCX-DASH-002 | v3/live? | | | | | | | | | | |
| HCX-003 | v1/status probe | | | | | | | | | | |
| HCX-DASH-001 | v1/status probe | | | | | | | | | | |
| `/models` 추가 발견 | auto registry | | | | | | | | | | |

## 3. 데이터셋별 상세 지표

### FAQ/코드

| 모델/설정 | FAQ EM | FAQ Fact Recall | FAQ Contradiction | 코드→사유 Acc | 사유→코드 Acc | 95% CI |
|---|---:|---:|---:|---:|---:|---|
| | | | | | | |

### RAG

| 모델/검색 | Recall@5 | MRR@10 | Citation P | Citation R | Faithfulness | Unsupported claims |
|---|---:|---:|---:|---:|---:|---:|
| | | | | | | |

### 구조화/도구

| 모델 | JSON parse | Schema valid | Required fields | Tool name Acc | Argument F1 | Unneeded calls |
|---|---:|---:|---:|---:|---:|---:|
| | | | | | | |

### 안전성

| 모델 | PII leak | Guarantee claim | Fabrication | Injection success | Unsafe advice | Over-refusal |
|---|---:|---:|---:|---:|---:|---:|
| | | | | | | |

### 운영

| 모델/설정·부하 | TTFT p50/p95/p99 | E2E p50/p95/p99 | TPOT p50/p95 | gap p95/p99 | max stall | tok/s | timeout | 429 | 5xx | Cost/request | Cost/correct |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | | | | | |

### 임베딩/API 도구

| 대상 | 품질 지표 | latency p50/p95/p99 | 처리량 | 오류율 | 추가 E2E 지연 | 장점 | 단점/제약 |
|---|---|---|---:|---:|---:|---|---|
| bge-m3 | | | | | | | |
| clir-emb-dolphin | | | | | | | |
| clir-sts-dolphin | | | | | | | |
| Reranker | | | | | | | |
| RAG Reasoning | | | | | | | |
| Router | | | | | | | |
| Summarization/Segmentation/Sliding/Skillset | | | | | | | |

## 4. HCX-007 Thinking 곡선

| Effort | Accuracy | Reasoning score | Avg thinking tokens | E2E p95 | Cost/correct | 상대 효율 |
|---|---:|---:|---:|---:|---:|---:|
| none | | | 0 또는 실제값 | | | 기준 |
| low | | | | | | |
| medium | | | | | | |
| high | | | | | | |

권장 선택 기준: `medium/high`가 `low` 대비 통계적으로 유의한 품질 향상을 만들지 못하면 운영 기본값으로 채택하지 않습니다.

## 5. Use-case 의사결정

| Use case | 후보 모델 | 최종 모델 | 필수 구성 | 근거 |
|---|---|---|---|---|
| 디폴트옵션 FAQ | DASH-002/005/007 | | RAG + citation | |
| 실물이전 코드 상담 | DASH-002/007 | | 룰 엔진 + LLM | |
| 투자설명서 질의 | 005/007 | | RAG + page citation | |
| 표·이미지 해석 | 005 | | Vision + 검증 | |
| 복합 규정 추론 | 007 | | Thinking + RAG + Guard | |
| JSON 업무 추출 | 007 | | Structured Outputs | |
| 대량 문서 분류 | DASH-002 | | batch + sampling QA | |

## 6. 실패 사례 기록

| Case ID | 모델 | 실패 유형 | 심각도 | 기대 결과 | 실제 결과 | 원인 가설 | 조치 |
|---|---|---|---|---|---|---|---|
| | | | critical/high/medium/low | | | | |

## 7. 최종 승인 체크리스트

- [ ] 모든 safety hard gate 통과
- [ ] Test split은 설정 확정 후 1회만 최종 평가
- [ ] 모델/API/프롬프트/데이터 버전 기록
- [ ] 전문가 검토 표본 크기 충족
- [ ] 평가자 일치도 목표 충족
- [ ] p95 latency와 오류율 SLO 충족
- [ ] 실제 계약 단가로 비용 계산
- [ ] 실패 사례와 제한사항 공개
- [ ] 고객-facing 응답에 Output Guard 적용
- [ ] Agent Trace와 Audit Trail 저장 검증

## 8. 결론 템플릿

```text
[모델/설정]은 [업무]에서 총점 [ ]점, safety gate [PASS/FAIL]를 기록했다.
비교 모델 대비 [정확도/지연/비용]에서 [효과 크기]의 차이가 있었고,
통계 검정 결과 [유의/비유의]했다.
따라서 [내부용/고객-facing/human-in-the-loop/적용 보류]로 결정한다.
주요 제한사항은 [ ]이며, 운영 전 [ ] 보완이 필요하다.
```
