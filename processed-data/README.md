# Processed Data — Test Build Entry Point

## 단일 진입 루트

서비스 테스트 빌드에서는 **이 README가 있는 디렉터리**를 단일 데이터 루트로 사용합니다. 저장 위치나 프로젝트 이름을 코드에 고정하지 말고, 배포 환경에서 `DATA_ROOT`로 주입합니다.

원본 파일 보관 위치는 이 데이터 패키지의 계약에 포함되지 않습니다. 검색·RAG·평가 입력은 아래에 정의한 `markdown/`과 `datasets/`만 사용합니다.

## 실제 로딩 대상

### 1. 문서 검색·RAG·질의응답 코퍼스

```text
markdown/**/*.md
```

- Markdown 158개
- 투자설명서 100개
- 연금·퇴직연금 업무 및 고객 안내 문서 58개
- PDF 6,625쪽의 페이지 경계 보존
- 각 파일 frontmatter에 원본 경로와 SHA-256 포함

로드 규칙:

- 확장자가 `.md`인 파일만 텍스트 로더로 읽습니다.
- `assets/`의 PNG/TMP 파일은 텍스트 로더에서 제외합니다.
- PDF 페이지 마커 `<!-- page: N -->`을 청크 경계로 우선 사용합니다.
- PPTX는 `<!-- Slide number: N -->`을 청크 경계로 사용합니다.
- XLSX Markdown은 `## Sheet N:`을 시트 경계로 사용합니다.

### 2. 구조화 FAQ·코드 테스트

```text
datasets/*.csv
```

- `default_option_faq_100.csv`: 디폴트옵션 FAQ 100건, 8컬럼
- `default_option_sources.csv`: 근거 출처 9건, 4컬럼
- `in_kind_transfer_restriction_reasons.csv`: 실물이전 불가사유 26건, 3컬럼

이 세 파일은 API Q&A 정확도 평가, 룰 기반 테스트, 검색 정답셋의 초기 소스로 사용합니다.

## 기본 테스트에서 제외할 영역

### `csv/`

XLSX 시트의 원래 행·열·빈 셀을 보존한 감사용 CSV입니다. `datasets/`와 내용이 중복되므로 일반 Q&A/RAG 테스트에 동시에 넣지 않습니다.

### `markdown/**/assets/`

원본 문서의 이미지·미디어입니다. 멀티모달 테스트가 아니면 텍스트 인덱싱에서 제외합니다. 이미지 중심 페이지의 Markdown에는 해당 asset 링크가 들어 있으므로 필요할 때만 비전 파이프라인으로 전달합니다.

## 추천 환경변수

```bash
# 실행 환경에서 이 README가 있는 디렉터리의 경로를 주입합니다.
DATA_ROOT="${DATA_ROOT:?Set DATA_ROOT to the processed-data directory}"
DOCUMENT_GLOB=markdown/**/*.md
STRUCTURED_GLOB=datasets/*.csv
```

Python 예시:

```python
import os
from pathlib import Path

data_root = Path(os.environ["DATA_ROOT"]).expanduser().resolve()
document_paths = sorted((data_root / "markdown").rglob("*.md"))
dataset_paths = sorted((data_root / "datasets").glob("*.csv"))
```

## 데이터 구성 요약

### A. 투자설명서 — 100개

종목코드별 펀드 투자설명서입니다.

- 상품 개요
- 운용 목적·전략
- 위험등급과 투자위험
- 수수료·보수
- 환매·과세
- 집합투자업자·판매회사
- 재무·운용 관련 공시성 정보

주 사용처: 펀드 상품 Q&A, 종목코드 기반 검색, 위험·비용·운용전략 비교.

### B. 연금·퇴직연금 업무 문서 — 58개

주요 주제:

1. 연금저축·개인연금·IRP 계좌 개요와 입출금
2. DB/DC/IRP 제도, 규약, 가입자교육, 부담금
3. 중도인출·계좌해지·압류·퇴직급여 청구
4. 연금수령·퇴직소득세·세액공제·과세이연
5. ISA 만기자금의 연금계좌 전환
6. 디폴트옵션 지정·옵트인·자동매수·FAQ
7. 실물이전 제도와 불가사유 코드
8. ETF·ETN·리츠·채권·주식적립식·유상청약 업무
9. 모바일/영업점 화면 및 처리 가이드
10. 포트폴리오·리밸런싱·MPS 서비스

주 사용처: 연금 상담 Agent, 내부 업무 지원, 고객 FAQ, 절세·제도 설명, 업무 프로세스 검색.

### C. 구조화 데이터셋 — 3개

정답 구조가 명확해 자동평가에 적합합니다.

- FAQ ID 1~100 검증 완료
- Source ID S1~S9 검증 완료
- 실물이전 코드 01~25, 99 검증 완료

## 전처리 품질 평가

### 통과 항목

- 원본 콘텐츠 파일 158개 → Markdown 158개
- 변환 오류 0개
- 원본 SHA-256 변경 없음
- PDF 6,625쪽 → 페이지 마커 6,625개 일치
- 투자설명서 내장 텍스트 페이지 누락 0건
- 텍스트 추출 실패 시각 페이지 7쪽은 렌더 이미지와 OCR 보조 텍스트 추가
- 실제 공백 페이지 1쪽 확인
- DOCX 미디어 참조 누락 0건
- PPTX 슬라이드 7개·내장 미디어 3개 추출, 미디어 3/3 시각 확인
- 구조화 CSV 행·컬럼·식별자 검증 PASS

### 주의 항목

1. OCR 문서 일부에는 띄어쓰기·문자 인식 오류가 남을 수 있습니다. 연결된 원본 페이지 이미지를 기준으로 판단합니다.
2. PDF 표는 텍스트 순서가 보존되어도 셀 구조가 평탄화될 수 있습니다.
3. PPTX는 서버 LibreOffice headless 로더 문제로 전체 슬라이드 렌더 이미지를 만들지 못했지만 텍스트·표·내장 미디어는 보존했습니다.
4. 서로 다른 상품 코드가 동일 SHA-256 문서를 가질 수 있으므로 내용 해시만으로 상품 레코드를 삭제하지 않습니다.
5. 규정·세법·상품 정보는 문서 기준시점이 있으므로 실제 고객 응답 전 기준일과 최신성 검증 계층이 필요합니다.

## 권장 테스트 순서

1. `datasets/default_option_faq_100.csv`로 정답형 API Q&A 테스트
2. `datasets/in_kind_transfer_restriction_reasons.csv`로 코드 질의 테스트
3. `markdown/docs/*.md`로 연금 업무 RAG 테스트
4. `markdown/투자설명서/**/*.md`로 종목코드·펀드 상품 Q&A 테스트
5. 전체 문서 통합 검색 테스트

## 청크 메타데이터 권장값

- `document_id`: 원본 상대경로 기반 ID
- `source_path`
- `source_sha256`
- `source_type`
- `document_group`: `docs` 또는 `투자설명서`
- `page` 또는 `slide`
- `sheet_name`
- `fund_code`
- `extraction_method`
- `chunk_text`

원본 SHA-256은 중복 감지용이며, 상품·문서의 유일 식별자로 단독 사용하지 않습니다.
