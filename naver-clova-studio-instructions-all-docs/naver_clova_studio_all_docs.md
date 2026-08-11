# NAVER CLOVA Studio API 전체 문서 수집본

- 출처: NAVER Cloud API 가이드
- 수집 시각: 2026-08-12T03:33:58+09:00
- 섹션 수: 11
- 문서 수: 31

## 수집 범위

- CLOVA Studio 개요: 1개
- Chat Completions V3: 4개
- Chat Completions: 1개
- 오픈AI 호환성: 1개
- 튜닝: 4개
- 익스플로러: 10개
- 라우터: 1개
- 스킬 트레이너: 1개
- CLOVA Studio 문제 해결: 6개
- CLOVA Studio Exclusive 지표: 1개
- CLOVA Studio 릴리스 노트: 1개

# CLOVA Studio 개요

## CLOVA Studio 개요

원문: https://api.ncloud-docs.com/docs/ai-naver-clovastudio-summary

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio는 초대규모(Hyperscale) AI 기술인 HyperCLOVA 언어 모델을 활용하여 사용자가 입력한 내용에 따라 AI 기술을 통해 생성된 문구를 출력하는 네이버 클라우드 플랫폼의 서비스입니다. CLOVA Studio 서비스에서는 문장 생성, 튜닝, 익스플로러, 라우터, 스킬 트레이너 기능에 대한 API를 RESTful 형태로 제공합니다.

API 키

CLOVA Studio API는 권한을 가진 사용자만 호출할 수 있도록 식별 도구인 API 키를 계정별로 발급하고 있습니다. API 키는 API 호출 시 인증 정보로 전달하는 요청 헤더의 파라미터로 사용합니다. 따라서 CLOVA Studio API를 사용하려면 우선 API 키를 발급받아야 합니다.

API 키 발급

API 키는 네이버 클라우드 플랫폼 콘솔의 CLOVA Studio에서 발급할 수 있습니다. 발급 방법은 다음과 같습니다.

네이버 클라우드 플랫폼 콘솔에 접속해 주십시오.
콘솔 화면 우측 상단의 리전 & 플랫폼 버튼을 클릭해 주십시오.
이용 중인 리전과 플랫폼을 선택한 후 [적용] 버튼을 클릭해 주십시오.
콘솔 화면 좌측 상단의 Menu를 클릭해 주십시오.
All Services > AI Services > CLOVA Studio 메뉴를 차례대로 클릭해 주십시오.
화면 좌측에서 API 키 메뉴를 클릭해 주십시오.
API 키 화면이 나타나면 발급할 API 키 탭 메뉴를 클릭한 다음 발급 버튼을 클릭해 주십시오.
테스트 API 키: [테스트] 탭 메뉴 클릭 > [테스트 API 키 발급] 버튼 클릭
서비스 앱을 제외한 CLOVA Studio API 호출 시 이용 가능
네이버 클라우드 플랫폼 메인 계정 기준 최대 10개까지 생성 가능
서비스 API 키: [서비스] 탭 메뉴 클릭 > [서비스 API 키 발급] 버튼 클릭
등록 완료된 서비스 앱의 CLOVA Studio API 호출 시 이용 가능
네이버 클라우드 플랫폼 메인 계정 기준 최대 10개까지 생성 가능
API 키 복사 팝업 창이 나타나면 [발급] 버튼을 클릭해 주십시오.
[복사] 버튼을 클릭한 다음 [완료] 버튼을 클릭해 주십시오.
주의

API 키 복사 팝업 창을 닫은 후에는 발급한 API 키 확인이 불가능합니다. 따라서 발급 시점에 반드시 별도의 안전한 공간에 보관하여 주십시오.

구 버전 API 키 확인 (Deprecated) 

2025년 1월 이전 발행한 테스트 앱 또는 등록한 서비스 앱에 대해 발급한 API 키를 확인할 수 있습니다.

테스트 앱

테스트 앱의 API 키를 확인하는 방법은 다음과 같습니다.

네이버 클라우드 플랫폼 콘솔에서 Menu > All Services > AI Services > CLOVA Studio 메뉴를 차례대로 클릭해 주십시오.
화면 좌측에서 API 키 메뉴를 클릭해 주십시오.
API 키 화면이 나타나면 [Deprecated] 탭 메뉴를 클릭해 주십시오.
을 클릭한 다음 복사 메뉴를 클릭하여 API 키를 확인해 주십시오.
우측 상단의 [API Gateway 키 보기] 버튼을 클릭해 주십시오.
API Gateway 키 팝업 창이 나타나면 API Gateway 키를 확인해 주십시오.
주의

API Gateway 키를 재발급하는 즉시 이전 키로 이용 중이었던 테스트 앱, 서비스 앱의 이용이 불가능해 집니다. 따라서 영향도 확인 및 사전 조치 후 반드시 필요한 경우에만 진행해 주십시오.

서비스 앱

서비스 앱의 API 키를 확인하는 방법은 다음과 같습니다.

네이버 클라우드 플랫폼 콘솔에서 Menu > All Services > AI Services > CLOVA Studio 메뉴를 차례대로 클릭해 주십시오.
화면 좌측에서 서비스 앱 신청 메뉴를 클릭해 주십시오.
서비스 앱의 코드 보기 버튼을 클릭해 주십시오.
[기존] 탭 메뉴를 클릭하여 서비스 앱의 구 버전 API 키를 확인한 다음 API Gateway 키를 확인해 주십시오.
API 키: X-NCP-CLOVASTUDIO-API-KEY
API Gateway 키: X-NCP-APIGW-API-KEY
API 보안 설정

API 키가 제3자에게 유출되는 경우, CLOVA Studio 리소스를 임의로 이용하는 등 보안 문제가 발생할 수 있으므로 적절한 사전 대비와 대응이 필요합니다.

API 키 삭제 및 재발급

API 키를 사용하지 않거나 제3자의 도용이 의심된다면 발급한 API 키를 삭제한 후 다시 발급해야 합니다. 삭제 및 재발급 방법은 다음과 같습니다.

네이버 클라우드 플랫폼 콘솔에서 Menu > All Services > AI Services > CLOVA Studio 메뉴를 차례대로 클릭해 주십시오.
화면 좌측에서 API 키 메뉴를 클릭해 주십시오.
API 키 화면이 나타나면 삭제할 API 키가 있는 탭 메뉴를 클릭해 주십시오.
삭제할 API 키의 을 클릭한 다음 삭제 메뉴를 클릭해 주십시오.
API 키 삭제 팝업 창이 나타나면 [삭제] 버튼을 클릭해 주십시오.
API 키 발급을 참조하여 새 API 키를 발급해 주십시오.
주의

삭제한 API 키는 유효하지 않은 키로 인식되기 때문에 더 이상 API 호출에 사용할 수 없습니다. 따라서 영향도 확인 및 사전 조치 후 반드시 필요한 경우에만 진행해 주십시오.

공통 설정

CLOVA Studio API에서 공통으로 사용하는 요청 형식과 응답 형식을 설명합니다.

참고

CLOVA Studio API 키가 있는 경우, 바로 CLOVA Studio API를 이용할 수 있습니다. 단, 서비스 API 키로 서비스 앱을 이용하기 위해서는 별도 신청 절차를 거쳐야 합니다. 신청 방법은 CLOVA Studio 사용 가이드
(opens in new tab)
를 참조해 주십시오.

요청

공통 요청 형식을 설명합니다.

API URL

요청 API URL은 다음과 같습니다.

Code snippet
https://clovastudio.stream.ntruss.com/

HTTP
COPY
참고

구 버전의 요청 API URL(https://clovastudio.apigw.ntruss.com/)도 CLOVA Studio API 호출에 사용할 수 있으나 지원 중단이 예정되어 있으므로 위에서 안내한 URL로 전환하는 것을 권장합니다. 구 버전의 요청 API URL로 호출 시 신규 API 키를 통한 인증이 불가능하며, 생성 토큰을 하나씩 출력하는 스트리밍 응답을 이용할 수 없습니다.

요청 헤더

요청 헤더에 대한 설명은 다음과 같습니다.

필드	필수 여부	설명 (예시)
Authorization	Required	인증을 위한 API 키
<예시> Bearer nv-************

X-NCP-CLOVASTUDIO-REQUEST-ID	Optional	요청에 대한 아이디
Content-Type	Required	요청 데이터의 형식
application/json

Accept	Conditional	응답 데이터의 형식
text/event-stream
참고

응답 결과는 기본적으로 JSON 형태로 반환되지만, Accept를 text/event-stream으로 지정 시 응답 결과를 스트림 형태로 반환합니다.

응답

공통 응답 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태
status.code	String	-	응답 상태 코드 참조
status.message	String	-	응답 메시지
result	Any	-	응답 결과
참고

응답 상태 코드별 원인 및 해결 방법은 CLOVA Studio 문제 해결을 참조해 주십시오.

응답 예시

응답 예시는 다음과 같습니다.

성공
Code snippet
{
  "status": {
    "code": "20000",
    "message": "OK"
  },
  "result": {}
}

JSON
COPY
실패
Code snippet
{
"status": {
    "code": "50000",
    "message": "Internal Server Error"
    }
}

JSON
COPY
실패 (오픈AI 호환성)
Code snippet
{
"error": {
    "message": "Internal Server Error",
    "type": null,
    "param": null, //미지원
    "code": "50000"
    }
}

JSON
COPY
CLOVA Studio API

CLOVA Studio에서 제공하는 API는 다음과 같습니다.

API	설명
Chat Completions v3 (텍스트 및 이미지)	비전/언어 모델을 활용한 이미지 해석 또는 대화형 문장 생성
Chat Completions v3 (추론(Thinking))	사용자 질의 분석과 논리적 사고를 통한 추론으로 최종 답변 생성
Chat Completions v3 (Fuction calling)	외부 함수 또는 API를 호출하여 동적으로 정보를 가져오거나 작업을 수행할 수 있는 Function calling
Chat Completions v3 (Structured Outputs)	원하는 JSON Schema 형식의 출력 결과를 생성할 수 있는 Structured Outputs
Chat Completions	HyperCLOVA X 모델을 활용한 대화형 문장 생성
오픈AI 호환성	주요 API에 대한 오픈AI SDK 및 API 호환성 제공
학습 조회	학습 현황 조회
학습 목록 조회	생성한 학습 목록 조회
학습 생성	사용자의 데이터셋을 사용한 학습 생성
학습 삭제	생성한 학습 삭제
리랭커	사용자 쿼리와 연관도 높은 검색 문서를 활용한 RAG 답변 생성
RAG Reasoning	RAG Reasoning 모델을 활용한 근거 기반 답변 생성
토큰 계산기(챗)	HCX 모델(Chat Completions API)에서 입력한 문장의 토큰 수 계산
토큰 계산기(챗 v3)	HCX 모델(Chat Completions v3 API)에서 입력한 문장 및 이미지의 토큰 수 계산
토큰 계산기(임베딩 v2)	임베딩 v2에서 입력한 문장의 토큰 수 계산
슬라이딩 윈도우	Chat Completions 이용 시 최대 토큰 수를 초과하는 문장 처리
요약	다양한 옵션을 적용하여 긴 문장 요약
임베딩	텍스트를 숫자로 표현하는 벡터화 작업 수행
임베딩 v2	장문 텍스트를 숫자로 표현하는 벡터화 작업 수행
문단 나누기	문장 간 유사도를 파악하여 주제 단위로 글의 단락 구분
라우터	사용자 입력에 대해 도메인과 필터 판별 수행
스킬셋	스킬셋 API 호출로 답변 생성
CLOVA Studio 연관 리소스

CLOVA Studio API에 대한 사용자의 이해를 돕기 위해 다양한 연관 리소스를 제공하고 있습니다.

CLOVA Studio API 사용 방법
API 개요: 네이버 클라우드 플랫폼에서 발급받은 Access Key, Secret Key 발급 및 확인, 요청 헤더에 필요한 서명 생성 방법
Sub Account 사용 가이드
(opens in new tab)
: 네이버 클라우드 플랫폼에서 발급받은 서브 계정의 Access Key 발급 및 확인 방법
CLOVA Studio 서비스 사용 방법
CLOVA Studio 사용 가이드
(opens in new tab)
: 네이버 클라우드 플랫폼 콘솔에서 CLOVA Studio 사용하는 방법
Ncloud 사용 환경 가이드
(opens in new tab)
: VPC, Classic 환경 및 지원 여부에 관한 사용 가이드
요금 소개, 특징, 상세 기능
(opens in new tab)
: CLOVA Studio의 요금 체계, CLOVA Studio의 특징, 상세 기능 및 활용 예시 요약
서비스 최신 소식
(opens in new tab)
: CLOVA Studio 관련 최신 소식
문의하기
(opens in new tab)
: 사용 가이드를 통해서도 궁금증이 해결되지 않는 경우 직접 문의
CLOVA Studio 포럼
(opens in new tab)
: CLOVA Studio 관련 공지, 활용법, 사용 경험 공유, 이용 문의

---

# Chat Completions V3

## 텍스트 및 이미지

원문: https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3

Classic/VPC 환경에서 이용 가능합니다.

이미지를 해석하고 이해할 수 있는 HCX-005 비전 모델과 경량화된 HCX-DASH-002 모델을 이용할 수 있는 v3 Chat Completions에 대해 설명합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	
/v3/chat-completions/{modelName}
모델을 사용하여 문장 생성
/v3/tasks/{taskId}/chat-completions
튜닝 학습한 작업을 사용하여 문장 생성
이미지 입력, 추론, Function calling, Structured Outputs 미지원
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	Enum	Required	모델 이름
<예시> HCX-005

taskId	String	Conditional	학습 아이디
튜닝 학습한 작업을 사용하여 문장 생성을 하려는 경우
학습 생성 참조
참고
HCX-005와 HCX-DASH-002는 Chat Completions v3 API에서만 사용할 수 있습니다.
이미지 입력은 HyperCLOVA X 비전 모델인 HCX-005에서만 사용할 수 있으며, 튜닝 학습은 지원하지 않습니다.
요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
messages	Array	Required	대화 메시지: messages
topP	Double	Optional	생성 토큰 후보군을 누적 확률을 기반으로 샘플링
0.00 ＜ topP ≤ 1.00 (기본값: 0.80)

topK	Integer	Optional	생성 토큰 후보군에서 확률이 높은 K개를 후보로 지정하여 샘플링
0 ≤ topK ≤ 128 (기본값: 0)

maxTokens	Integer	Optional	최대 생성 토큰 수
1 ≤ maxTokens ≤ 모델 최대값
maxCompletionTokens와 동시에 사용 불가

maxCompletionTokens	Integer	Optional	최대 생성 토큰 수 (추론 모델)
1 ≤ maxCompletionTokens ≤ 모델 최대값
maxTokens와 동시에 사용 불가

temperature	Double	Optional	생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성)
0.00 ≤ temperature ≤ 1.00 (기본값: 0.50)

repetitionPenalty	Double	Optional	같은 토큰을 생성하는 것에 대한 패널티 정도
0.0 ＜ repetitionPenalty ≤ 2.0 (기본값: 1.1)
설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소
1.0~1.1에서 0.05 단위로 미세 조정 권장

stop	Array	Optional	토큰 생성 중단 문자
[](기본값)
추론 시 사용 불가

seed	Integer	Optional	모델 반복 실행 시 결괏값의 일관성 수준 조정
0: 일관성 수준 랜덤 적용 (기본값)
1 ≤ seed ≤ 4294967295: 일관되게 생성하고자 하는 결괏값의 seed 값 또는 사용자가 지정하고자 하는 seed 값

includeAiFilters	Boolean	Optional	AI 필터(생성된 결괏값에 대해 욕설, 비하/차별/혐오, 성희롱/음란 등 카테고리별로 해당하는 정도) 결과 표시 여부
true | false (기본값)
true: 표시
false: 표시 안 함
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 사용자의 발화 또는 질문에 대한 답변

content	String | Array	Required	대화 메시지 내용
텍스트 입력(String)
텍스트, 이미지 URL로 구성하여 입력(Array): content
content

content에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
type	Enum	Required	대화 메시지 내용의 형식
text | image_url
text : 텍스트
image_url : 이미지 URL

text	String	Conditional	대화 메시지 내용
텍스트 입력
type이 text인 경우, 필수 입력

imageUrl	Object	Conditional	이미지 목록
type이 image_url인 경우, imageUrl과 dataUri 중 필수 입력
턴당 이미지 1개 포함 가능
최적의 결과를 위해 text와 함께 요청 권장

imageUrl.url	String	Conditional	파일 확장자를 포함한 단일 이미지의 공개 URL
이미지 지원 사양
형식: BMP, PNG, JPG, JPEG, WEBP
크기: 0Byte 초과 20MB 이하
비율: 가로, 세로가 1:5 또는 5:1 이하
길이: 가로, 세로 중 긴 쪽은 2240px이하. 짧은 쪽은 4px 이상

dataUri	Object	Conditional	이미지 목록
type이 image_url인 경우, imageUrl과 dataUri 중 필수 입력
턴당 이미지 1개 포함 가능
최적의 결과를 위해 text와 함께 요청 권장

dataUri.data	String	Conditional	Base64로 인코딩된 이미지 문자열
이미지 지원 사양
형식: BMP, PNG, JPG, JPEG, WEBP
크기: 0Byte 초과 20MB 이하
비율: 가로, 세로가 1:5 또는 5:1 이하
길이: 가로, 세로 중 긴 쪽은 2240px이하. 짧은 쪽은 4px 이상
참고

일부 필드 입력 시 다음 내용을 확인해 주십시오.

role: system인 대화 메시지는 요청당 1개만 포함할 수 있습니다.
HCX-005
입력 토큰과 출력 토큰의 합은 128000 토큰을 초과할 수 없습니다.
입력 토큰은 최대 128000 토큰까지 가능합니다.
모델에 요청할 출력 토큰(maxTokens)은 최대 4096 토큰까지 가능합니다.
messages: 턴 당 이미지는 1개 포함 가능하고, 요청당 이미지는 최대 5개 포함할 수 있습니다.
전체 Request Body 크기는 50MB 이하여야 합니다. 따라서 여러 개의 이미지를 요청에 포함하는 경우 base64 형식보다 image URL 사용을 권장합니다.
HCX-DASH-002
입력 토큰과 출력 토큰의 합은 32000 토큰을 초과할 수 없습니다.
입력 토큰은 최대 32000 토큰까지 가능합니다.
모델에 요청할 출력 토큰(maxTokens)은 최대 4096 토큰까지 가능합니다.
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005' \
--header 'Authorization: Bearer {CLOVA Studio API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--header 'Accept: text/event-stream' \
--data '{
    "messages": [
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "- 친절하게 답변하는 AI 어시스턴트입니다."
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "imageUrl": {
              "url": "https://www.******.com/image_a1b1c1.png"
            }
          },
          {
            "type": "text",
            "text": "이 사진에 대해서 설명해줘"
          }
        ]
      }
    ],
    "topP": 0.8,
    "topK": 0,
    "maxTokens": 100,
    "temperature": 0.5,
    "repetitionPenalty": 1.1,
    "stop": []
  }'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참
result	Object	-	응답 결과
result.created	Integer	-	응답 날짜
Unix timestamp miliseconds 형식

result.usage	Object	-	토큰 사용량
result.usage.completionTokens	Integer	-	생성 토큰 수
result.usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
result.usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수

result.message	Object	-	대화 메시지
result.message.role	Enum	-	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

result.message.content	String	-	대화 메시지 내용
result.finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop | tool_calls
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현
tool_calls: 모델이 정상적으로 도구 호출 완료

result.seed	Integer	-	입력 seed 값(0 입력 또는 미입력 시 랜덤 값 반환)
result.aiFilter	Array	-	AI 필터 결과: aiFilter
aiFilter

aiFilter에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
groupName	String	-	AI 필터 카테고리
curse | unsafeContents
curse: 비하, 차별, 혐오 및 욕설
unsafeContents: 성희롱, 음란

name	String	-	AI 필터 세부 카테고리
discrimination | insult | sexualHarassment
discrimination: 비하, 차별, 혐오
insult: 욕설
sexualHarassment: 성희롱, 음란

score	String	-	AI 필터 점수
-1 | 0 | 1 | 2
-1: AI 필터 오류 발생
0: 대화 메시지에 민감/위험 표현 포함 가능성 높음
1: 대화 메시지에 민감/위험 표현 포함 가능성 있음
2: 대화 메시지에 민감/위험 표현 포함 가능성 낮음

result	String	-	AI 필터 정상 작동 여부
OK | ERROR
OK: 정상 작동
ERROR: 오류 발생
참고

AI Filter는 최대 500자까지 분석할 수 있습니다. 단, 분석 대상 텍스트에 비정상적인 형식, 이모티콘, 특수 문자 등이 많은 경우, 정상적으로 분석되지 않을 수 있습니다.

응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "created": 1791043155000,
        "usage": {
            "completionTokens": 80,
            "promptTokens": 843,
            "totalTokens": 923
        },        
        "message": {
            "role": "assistant",
            "content": "사진에는 어린 아이가 양에게 먹이를 주는 모습이 담겨 있습니다. 아이는 파란색 옷을 입고 있으며, 줄문의 모자를 쓰고 있습니다. 아이의 표정은 집중하고 있는 듯 보이며, 양은 아이가 주는 먹이를 먹으려고 머리를 숙이고 있습니다. 배경에는 다른 양들도 보이며, 이 장소가 양 목장임을 짐작할 수 있습니다."
        },
        "seed": 1561390649,
        "aiFilter": [
         {
          "groupName": "curse",
          "name": "insult",
         "score": "1"
         },
         {
          "groupName": "curse",
          "name": "discrimination",
          "score": "0"
         },
         {
          "groupName": "unsafeContents",
          "name": "sexualHarassment",
          "score": "2"
         }
        ]
    }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)
응답 스트림

생성되는 토큰을 하나씩 출력하도록 토큰 스트리밍을 사용할 수 있습니다. 토큰 스트리밍 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Accept	-	응답 데이터의 형식
text/event-stream
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

StreamingChatCompletionsTokenEvent

StreamingChatCompletionsTokenEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
created	Integer	-	응답 시간 타임스탬프
usage	Object	-	토큰 사용량
usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
usage.completionTokens	Integer	-	생성 토큰 수
message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현
StreamingChatCompletionsResultEvent

StreamingChatCompletionsResultEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
created	Integer	-	응답 시간 타임스탬프
usage	Object	-	토큰 사용량
usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
usage.completionTokens	Integer	-	생성 토큰 수
usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수

message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현

aiFilter	Array	-	AI 필터 결과: aiFilter
ErrorEvent

ErrorEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태
status.code	Object	-	응답 상태 코드
CLOVA Studio 문제 해결 참조

status.message	Object	-	응답 상태 메시지
CLOVA Studio 문제 해결 참조
SignalEvent

SignalEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
data	String	-	전달할 시그널 데이터 정보
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
id: aabdfe-dfgwr-edf-hpqwd-f3asd-g
event: token
data: {"message": {"role": "assistant", "content": “안”},"finishReason": null, "created": 1744710905, "seed": 3284419119, "usage": null} 

id: aabdfe-dfgwr-edf-hpqwd-f2asd-g
event: token
data: {"message": {"role": "assistant", "content": “녕”},"finishReason": null, "created": 1744710905, "seed": 3284419119, "usage": null} 

id: aabdfe-dfgwr-edf-hpqwd-f1asd-g
event: result
data: {"message": {"role": "assistant", "content": “안녕”}, "finishReason": "stop", "created": 1744710905, "seed": 3284419119, "usage": {"promptTokens": 20, "completionTokens": 5, "totalTokens": 25}}

Python
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 추론(Thinking)

원문: https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3-thinking

Classic/VPC 환경에서 이용 가능합니다.

복잡한 문제 해결 능력을 갖춘 HCX-007 추론 모델을 이용할 수 있는 v3 Chat Completions에 대해 설명합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v3/chat-completions/{modelName}
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	Enum	Required	모델 이름
<예시> HCX-007
참고

HCX-007 추론 모델은 Chat Completions v3 API에서만 사용할 수 있으며, 이미지 입력과 튜닝 학습은 지원하지 않습니다.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
messages	Array	Required	대화 메시지
thinking	Object	Optional	추론 모델 설정 정보
thinking.effort	Enum	Optional	추론 여부 및 사고 과정 깊이 설정
none | low (기본값) | medium |high
none: 추론 안 함
low: 짧은 추론
medium: 중간 길이 추론
high: 긴 추론

topP	Double	Optional	생성 토큰 후보군을 누적 확률을 기반으로 샘플링
0.00＜topP ≤ 1.00 (기본값: 0.80)

topK	Integer	Optional	생성 토큰 후보군에서 확률이 높은 K개를 후보로 지정하여 샘플링
0 ≤ topK ≤ 128 (기본값: 0)

maxCompletionTokens	Integer	Optional	최대 생성 토큰 수 (추론 내용을 포함한 대화 메시지 길이)
1 ≤ maxCompletionTokens ≤ 32768 (기본값: thinking.effort에 따라 상이)
none: 512
low: 5120
medium: 10240
high: 20480
maxTokens 사용 불가

temperature	Double	Optional	생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성)
0.00 ≤ temperature ≤ 1.00 (기본값: 0.50)

repetitionPenalty	Double	Optional	같은 토큰을 생성하는 것에 대한 패널티 정도
0.0 ＜ repetitionPenalty ≤ 2.0 (기본값: 1.1)
설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소
1.0~1.1에서 0.05 단위로 미세 조정 권장

seed	Integer	Optional	모델 반복 실행 시 결괏값의 일관성 수준 조정
0: 일관성 수준 랜덤 적용 (기본값)
1 ≤ seed ≤ 4294967295: 일관되게 생성하고자 하는 결괏값의 seed 값 또는 사용자가 지정하고자 하는 seed 값

includeAiFilters	Boolean	Optional	AI 필터(생성된 결괏값에 대해 욕설, 비하/차별/혐오, 성희롱/음란 등 카테고리별로 해당하는 정도) 결과 표시 여부
true | false (기본값)
true: 표시
false: 표시 안 함
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 사용자의 발화 또는 질문에 대한 답변

content	String | Array	Required	대화 메시지 내용
텍스트 입력(String)
텍스트 입력(Array): content
content

content에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
type	Enum	Required	대화 메시지 내용의 형식
text (유효 값)

text	String	Conditional	대화 메시지 내용
텍스트 입력
type이 text인 경우, 필수 입력
참고

일부 필드 입력 시 다음 내용을 확인해 주십시오.

role: system인 대화 메시지는 요청당 1개만 포함할 수 있습니다.
role: assistant인 대화 메시지 입력 시 message.thinkingContent는 요청에 포함할 수 없습니다.
추론과 Function calling 또는 Structured Outputs를 동시에 요청할 수 없습니다.
추론 사용 시 Chat Completions V3의 stop은 사용할 수 없습니다.
HCX-007
입력 토큰과 출력 토큰의 합은 128000 토큰을 초과할 수 없습니다.
입력 토큰은 최대 128000 토큰까지 가능합니다.
모델에 요청할 출력 토큰(maxCompletionTokens)은 최대 32768 토큰까지 설정 가능합니다.
요청 예시

요청 예시는 다음과 같습니다.

curl --location --request POST 'https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-007' \
--header 'Authorization: Bearer {CLOVA Studio API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--header 'Accept: text/event-stream' \
--data '{
    "messages": [
      {
        "role": "system",
        "content": "- 고도로 체계적인 분석가이자 논리 기반 문제 해결의 전문가입니다."
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "n개의 원소를 가진 집합이 있을 때, 이 집합에서 만들 수 있는 모든 부분집합의 개수가 2의 n제곱과 같다는 것을 설명하라."
          }
        ]
      }
    ],
    "thinking": {
        "effort": "low"
        },
    "topP": 0.8,
    "topK": 0,
    "maxCompletionTokens": 5120,
    "temperature": 0.5,
    "repetitionPenalty": 1.1
  }'

응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.message	Object	-	대화 메시지
result.message.role	Enum	-	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

result.message.content	String	-	대화 메시지 내용
result.message.thinkingContent	String	-	대화 메시지 중 추론 내용
result.finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현
tool_calls: 모델이 정상적으로 도구 호출 완료

result.created	Integer	-	응답 날짜
Unix timestamp miliseconds 형식

result.seed	Integer	-	입력 seed 값(0 입력 또는 미입력 시 랜덤 값 반환)
result.usage	Object	-	토큰 사용량
result.usage.completionTokens	Integer	-	생성 토큰 수
result.usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
result.usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수

result.usage.completionTokensDetails	Object	-	생성 토큰 수 관련 추가 정보
result.usage.completionTokensDetails.thinkingTokens	Integer	-	추론 토큰 수
result.aiFilter	Array	-	AI 필터 결과: aiFilter
aiFilter

aiFilter에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
groupName	String	-	AI 필터 카테고리
curse | unsafeContents
curse: 비하, 차별, 혐오 및 욕설
unsafeContents: 성희롱, 음란

name	String	-	AI 필터 세부 카테고리
discrimination | insult | sexualHarassment
discrimination: 비하, 차별, 혐오
insult: 욕설
sexualHarassment: 성희롱, 음란

score	String	-	AI 필터 점수
-1 | 0 | 1 | 2
-1: AI 필터 오류 발생
0: 대화 메시지에 민감/위험 표현 포함 가능성 높음
1: 대화 메시지에 민감/위험 표현 포함 가능성 있음
2: 대화 메시지에 민감/위험 표현 포함 가능성 낮음

result	String	-	AI 필터 정상 작동 여부
OK | ERROR
OK: 정상 작동
ERROR: 오류 발생
참고

AI Filter는 최대 500자까지 분석할 수 있습니다. 단, 분석 대상 텍스트에 비정상적인 형식, 이모티콘, 특수 문자 등이 많은 경우, 정상적으로 분석되지 않을 수 있습니다.

응답 예시 

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "message": {
            "role": "assistant",
            "content": "부분집합의 개수는 각 원소가 포함 또는 제외되는 두 가지 선택으로 결정됩니다.\n예를 들어, {a}의 부분집합은 ∅, {a} → 2개 (2¹)이며,
{a,b}는 ∅, {a}, {b}, {a,b} → 4개 (2²)입니다.\nn개 원소 집합에서는 각 원소마다 2가지 선택지(포함/제외)가 있으므로, 전체 경우의 수는 2 × 2 × ... × 2 (n번) = 2ⁿ이 됩니다.\n또는 이항정리로도 설명 가능합니다: 부분집합의 크기가 k인 경우의 수는 조합 **C(n,k)**이므로, 모든 k(0 ≤ k ≤ n)에 대해 합하면 ∑_{k=0}^n C(n,k) = (1+1)^n = 2ⁿ입니다.\n따라서 n개 원소의 부분집합 개수는 항상 2ⁿ입니다.",
            "thinkingContent": "오늘 사용자가 물어본 문제는 n개의 원소를 가진 집합에서 만들 수 있는 모든 부분집합의 개수가 왜 2의 n제곱인지 설명해달라는 거야. 이 주제는 조합론이나 이진법과 관련이 있지 않을까?\n먼저, 각 원소에 대해 선택하거나 선택하지 않는 두 가지 경우가 있다는 걸 생각해봐. 예를 들어 원소가 하나라면 부분집합은 공집합과 그 자체로 총 2개, 즉 2^1=2개가 되지. 원소가 둘일 때는 각각 포함되거나 안 되니까 2*2=4개, 2^2=4가 되고.\n일반화하면 각 원소마다 2가지 선택(포함/제외)이 가능하니까 전체 경우의 수는 2를 n번 곱한 것, 즉 2^n이 되는 거야. 이게 기본적인 조합적 사고 방식이지.\n혹은 부분집합의 크기가 k인 경우의 수를 생각하면 C(n,k)이고, 이를 k=0부터 n까지 더하면 (1+1)^n = 2^n이 된다는 이항정리도 떠올라. 그래서 모든 부분집합의 수는 2^n이라는 결론에 도달할 수 있어.\n사용자가 이 설명을 원했을 테니 간결하게 각 원소의 선택 여부로 접근하는 게 좋을 것 같아. 예시를 들어 설명하고, 일반화하는 과정을 짧게 요약해야겠어."
        },
        "finishReason": "stop",
        "created": 1753362971,
        "seed": 1561390649,
        "usage": {
            "promptTokens": 58,
            "completionTokens": 631,
            "totalTokens": 689,
            "completionTokensDetails": {
                "thinkingTokens": 366
            }
}

실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)
응답 스트림

생성되는 토큰을 하나씩 출력하도록 토큰 스트리밍을 사용할 수 있습니다. 토큰 스트리밍 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

StreamingChatCompletionsTokenEvent

StreamingChatCompletionsTokenEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
message.thinkingContent	String	-	대화 메시지 중 추론 내용
finishReason	String	-	토큰 생성 중단 이유 (일반적으로 마지막 이벤트에 전달, 그 외 null)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현

created	Integer	-	응답 시간 타임스탬프
seed	Integer	-	입력 seed 값 (0 입력 또는 미입력 시 랜덤 값 반환)
usage	Object	-	토큰 사용량 (일반적으로 마지막 이벤트에 전달, 그 외 null)
StreamingChatCompletionsResultEvent

StreamingChatCompletionsResultEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
message.thinkingContent	String	-	대화 메시지 중 추론 내용
finishReason	String	-	토큰 생성 중단 이유
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현

created	Integer	-	응답 시간 타임스탬프
seed	Integer	-	입력 seed 값 (0 입력 또는 미입력 시 랜덤 값 반환)
usage	Object	-	토큰 사용량
usage.completionTokens	Integer	-	생성 토큰 수
usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수

usage.completionTokensDetails	Object	-	생성 토큰 수 관련 추가 정보
usage.completionTokensDetails.thinkingTokens	Integer	-	추론 토큰 수
aiFilter	Array	-	AI 필터 결과: aiFilter
ErrorEvent

ErrorEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
status.code	Object	-	응답 상태 코드
CLOVA Studio 문제 해결 참조

status.message	Object	-	응답 상태 메시지
CLOVA Studio 문제 해결 참조
SignalEvent

SignalEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
data	String	-	전달할 시그널 데이터 정보
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

id: aabdfe-dfgwr-edf-hpqwd-f3asd-g
event: token
data: {"message": {"role": "assistant", "thinkingContent": “오늘”},"finishReason": null, "created": 1744710905, "seed": 3284419119, "usage": null} 

...

id: aabdfe-dfgwr-edf-hpqwd-f2asd-g
event: token
data: {"message": {"role": "assistant", "content": “부분”},"finishReason": null, "created": 1744710905, "seed": 3284419119, "usage": null} 

...

id: aabdfe-dfgwr-edf-hpqwd-f1asd-g
event: result
data: {
    "message": {
        "role": "assistant",
        "content": "부분집합의 수는 각 원소의 **포함 여부**에 따라 결정됩니다.  \n각 원소는 **\"포함\" 또는 \"미포함\"** 중 하나를 선택할 수 있으므로, 한 원소당 2가지 경우가 생깁니다.  \n\n예를 들어:  \n- 원소가 하나인 집합({a}) → ∅, {a} (**2¹ = 2**)  \n- 원소가 둘인 집합({a, b}) → ∅, {a}, {b}, {a,b} (**2² = 4**)  \n\n확장하면, **n개 원소**는 각 단계마다 이전 결과(2ⁿ⁻¹)에 **2배**씩 증가합니다(**2ⁿ⁻¹ × 2 = 2ⁿ**).  \n즉, 모든 부분집합의 수는 **2ⁿ**으로 표현되며, 이는 각 원소의 독립적 선택 가능성을 반영한 것입니다.  \n\n공집합과 전체 집합 역시 자연스럽게 포함되므로, 공식 **2ⁿ**은 완전하고 일관된 결과를 제공합니다.",
        "thinkingContent": "오늘 사용자가 물어본 문제는 n개의 원소로 이루어진 집합의 부분집합의 수가 왜 2^n인지 설명해달라는 거야. 이걸 어떻게 쉽게 설명할 수 있을까? \n\n먼저 기본 개념부터 생각해보자. 각 원소는 부분집합에 포함되거나 포함되지 않거나 두 가지 선택지가 있지. 예를 들어 원소가 하나라면 {}, {a} 두 개의 부분집합이야. 여기서 2^1=2로 맞아떨어져.\n\n두 번째 원소 b를 추가하면 각각의 기존 부분집합에 대해 b를 넣을지 말지 결정해야 해. 원래 {}와 {a} 각각에 대해 b를 추가하거나 안 하니까 총 4개가 되겠지. 이건 2^2=4고. 이런 식으로 확장되면 n개일 때는 각 단계마다 이전 경우의 수에 2를 곱하는 게 반복되니까 결국 2×2×…×2 (n번) = 2^n이 되는 거야.\n\n또 다른 접근은 각 원소에 대한 독립적 선택을 강조하는 거야. 각 원소의 포함 여부가 서로 영향을 주지 않으므로 조합의 곱셈 법칙을 적용할 수 있어. 따라서 전체 경우의 수는 2 × 2 × … × 2 (n번) = 2^n으로 계산되는 거지.\n\n혹시 공집합이나 전체 집합도 포함된다는 걸 언급해야 할까? 예제를 통해 보여주면 더 명확해질 것 같아. 하지만 간결하게 설명하려면 핵심 아이디어인 각 원소의 선택 가능성만 강조해도 충분하지 않을까?\n\n마지막으로 수학적으로 엄밀히 증명하기 위해 귀납법을 사용할 수도 있지만, 사용자의 요청은 간단한 설명을 원하는 것 같으니 기본적인 논리를 중심으로 답변해야겠다. 이렇게 생각하면 될 것 같다!"
    },
    "finishReason": "stop",
    "created": 1753363313,
    "seed": 3219533885,
    "usage": {
        "promptTokens": 58,
        "completionTokens": 588,
        "totalTokens": 646,
        "completionTokensDetails": {
            "thinkingTokens": 361
        }
    }
}

실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)
권장 사항

CLOVA Studio 추론 모델은 최종 답변을 바로 생성하지 않고, 사용자 질의를 분석하고 필요한 논리적 사고 과정을 거쳐 추론 내용(토큰)을 생성한 뒤 이를 바탕으로 최종 답변을 생성합니다. 권장 사항에서는 최적화된 최종 답변 생성을 위해 추론 모델을 효과적으로 활용하는 방법을 설명합니다.

추론 여부 및 길이 설정

CLOVA Studio 추론 모델은 사용자가 직접 추론 여부와 길이를 설정할 수 있도록 학습되어 있습니다. 다음 설정 방법을 참고하여 요청 종류에 맞게 추론 여부 및 길이를 설정해 주십시오.

추론 여부와 추론의 사고 과정 깊이
thinking.effort를 통해 설정합니다. 설정값에 따라 최대 생성 요청 토큰 수의 기본값이 다음과 같이 적용됩니다.
thinking.effort 설정값	maxCompletionTokens 기본값	설명
none	512	추론 사용 안 함
low	5120	짧은 길이의 추론 (기본값)
medium	10240	중간 길이의 추론
high	20480	긴 길이의 추론
추론 길이(최대 생성 토큰 수)
maxCompletionTokens를 통해 설정합니다. 추론 내용과 최종 답변 토큰 수를 전부 포함합니다.
추론에서는 maxTokens가 아닌 maxCompletionTokens를 사용합니다.
값을 직접 설정할 수 있지만, 설정값이 충분히 크지 않은 경우에 모델이 추론 과정 중 해당 길이에 도달하게 되면 최종 답변을 생성하지 못할 수 있습니다. 따라서 기본값을 준수하거나 여러 번 시도를 통해 적절한 길이를 찾아 설정해 주십시오.
참고

상대적으로 긴 출력값을 생성하려면 일정 시간이 소요될 수 있으므로 스트림 출력 설정을 권장합니다.

추론 내용 확인

추론을 사용한 API 요청 시 응답 결과에는 추론 내용과 최종 답변이 각각 구성되어 출력됩니다. 추론 내용 및 토큰 수는 다음과 같이 확인할 수 있습니다.

추론 모델이 최종 답변을 위해 생성한 생각 과정을 담은 추론 내용은 응답 바디의 message.thinkingContent에서 확인할 수 있습니다.
추론 내용의 토큰 수는 응답 바디의 usage.completionTokensDetails.thinkingTokens에서 확인할 수 있습니다.
주의

추론 내용은 좀 더 나은 최종 답변을 얻기 위한 과정으로 시스템 프롬프트를 비롯한 모델에 전달된 컨텍스트 일부가 포함될 수 있습니다. 따라서 추론 내용은 개발 목적으로만 활용하는 것을 권장하며, 별도의 후처리 없이 사용자에게 제공하는 것은 지양해 주십시오.

멀티 턴 대화 시 입력 처리

멀티 턴 대화를 이어가려고 하는 경우, CLOVA Studio 추론 모델의 추론 내용(message.thinkingContent)은 제외하고 최종 답변인 모델 응답(message.content)만 다음 턴 입력에 포함해야 합니다. 다음 그림을 참고해 주십시오.

---

## Function calling

원문: https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3-fc

Classic/VPC 환경에서 이용 가능합니다.

Function calling을 지원하여 외부 함수나 API 호출을 통해 동적으로 정보를 가져오거나 작업을 수행할 수 있는 v3 Chat Completions에 대해 설명합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v3/chat-completions/{modelName}
참고

HyperCLOVA X Function calling은 Chat Completions v3, 오픈AI 호환 API에서만 사용할 수 있으며, 튜닝 모델의 경우에는 지원하지 않습니다.

요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	Enum	Required	모델 이름
<예시> HCX-005
요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
messages	Array	Required	대화 메시지: messages
topP	Double	Optional	생성 토큰 후보군을 누적 확률을 기반으로 샘플링
0.00 ＜ topP ≤ 1.00 (기본값: 0.8)
최종 텍스트 응답 반환 시에만 적용 (대화 메시지의 role이 tool인 경우)

topK	Integer	Optional	생성 토큰 후보군에서 확률이 높은 K개를 후보로 지정하여 샘플링
0 ≤ topK ≤ 128 (기본값: 0)
최종 텍스트 응답 반환 시에만 적용 (대화 메시지의 role이 tool인 경우)

maxTokens	Integer	Optional	최대 생성 토큰 수
1024≤ maxTokens ≤ 모델 최대값
maxCompletionTokens와 동시 사용 불가

maxCompletionTokens	Integer	Optional	최대 생성 토큰 수 (추론 모델)
1024≤ maxCompletionTokens ≤ 모델 최대값
maxTokens와 동시 사용 불가

temperature	Double	Optional	생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성)
0.00 ≤ temperature ≤ 1.00 (기본값: 0.5)
최종 텍스트 응답 반환 시에만 적용 (대화 메시지의 role이 tool인 경우)

repetitionPenalty	Double	Optional	같은 토큰을 생성하는 것에 대한 패널티 정도
0.0 ＜ repetitionPenalty ≤ 2.0 (기본값: 1.1)
설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소
1.0~1.1에서 0.05 단위로 미세 조정 권장
최종 텍스트 응답 반환 시에만 적용 (대화 메시지의 role이 tool인 경우)

stop	Array	Optional	토큰 생성 중단 문자
[](기본값)
최종 텍스트 응답 반환 시에만 적용 (대화 메시지의 role이 tool인 경우)

thinking	Object	Optional	추론 모델 설정 정보
thinking.effort	String	Optional	추론 여부 및 사고 과정 깊이 설정
none (유효 값)
Function calling과 동시 사용 불가

tools	Array	Optional	Function calling 사용 가능 도구 목록: tools
toolChoice	String | Object	Optional	Function calling 도구 호출 동작 방식
auto : 모델이 도구 자동 호출 (String)
none : 모델이 도구 호출 없이 일반 답변 생성 (String)
모델이 특정 도구 강제 호출 (Object)

toolChoice.type	String	Optional	Function calling 모델이 호출할 도구 유형
toolChoice.function	Object	Optional	Function calling 모델이 호출할 도구
function (유효 값)

toolChoice.function.name	String	Optional	Function calling 모델이 호출할 도구 이름
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
system | user | assistant | tool
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 사용자의 발화 또는 질문에 대한 답변
tool: assistant(모델)가 호출한 함수의 실행 결과

content	String	Required	대화 메시지 내용
텍스트 입력(String)

toolCalls	Array	Conditional	assistant의 호출 도구 정보
role이 tool인 경우, assistant의 toolCalls 요청과 같이 입력

toolCallId	String	Conditional	도구 아이디
role이 tool인 경우, 필수 입력
assistant의 toolCalls 요청과 연결하는 용도
tools

tools에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
type	String	Required	도구 유형
function(유효 값)

function	Object	Required	호출 function 정보
function.name	String	Required	function 이름
function.description	String	Required	function 설명
function.parameters	Object	Optional	function 사용 시 전달되는 매개변수
properties, required
입력: 동작 방식 참조
형식: JSON Schema reference
(opens in new tab)
 참조
toolCalls

toolCalls에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	도구 식별자
type	String	-	도구 유형
function(유효 값)

function	Object	-	호출 function 정보
function.name	String	-	function 이름
function.arguments	Object	-	function 사용 시 전달되는 매개변수
참고

일부 필드 입력 시 다음 내용을 확인해 주십시오.

role: system인 대화 메시지는 요청당 1개만 포함할 수 있습니다.
Fuction calling은 추론 또는 이미지 해석과 동시에 요청할 수 없습니다.
Function calling은 결괏값 생성 시 사용하는 최대 토큰 수(maxTokens 또는 maxCompletionTokens)를 1024 이상으로 설정해 주십시오.
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.created	Integer	-	응답 날짜
Unix timestamp miliseconds 형식

result.usage	Object	-	토큰 사용량
result.usage.completionTokens	Integer	-	생성 토큰 수
result.usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
result.usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수

result.message	Object	-	대화 메시지
result.message.role	Enum	-	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

result.message.content	String	-	대화 메시지 내용
result.message.toolCalls	Array	-	toolCalls
result.finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop| tool_calls
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현
tool_calls: 모델이 정상적으로 도구 호출 완료

result.seed	Integer	-	입력 seed 값(0 입력 또는 미입력 시 랜덤 값 반환)
toolCalls

toolCalls에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	도구 식별자
type	String	-	도구 유형
function(유효 값)

function	Object	-	호출 function 정보
function.name	String	-	function 이름
function.arguments	Object	-	function 사용 시 전달되는 매개변수
응답 스트림

생성되는 토큰을 하나씩 출력하도록 토큰 스트리밍을 사용할 수 있습니다. 토큰 스트리밍 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Accept	-	응답 데이터의 형식
text/event-stream
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

StreamingChatCompletionsTokenEvent

StreamingChatCompletionsTokenEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
created	Integer	-	응답 시간 타임스탬프
usage	Object	-	토큰 사용량
usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
usage.completionTokens	Integer	-	생성 토큰 수
message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
message.toolCalls	Array	-	toolCalls
finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현
toolCalls

StreamingChatCompletionsTokenEvent에서의 toolCalls에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	도구 식별자
type	String	-	도구 유형
function(유효값)

function	Object	-	호출 function 정보
function.name	String	-	function 이름
function.partialJson	String	-	function 에 전달할 JSON 인자를 구성하는 문자열의 일부
StreamingChatCompletionsResultEvent

StreamingChatCompletionsResultEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
created	Integer	-	응답 시간 타임스탬프
usage	Object	-	토큰 사용량
usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
usage.completionTokens	Integer	-	생성 토큰 수
usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수

message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
message.toolCalls	Array	-	toolCalls
finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현
tool_calls: 모델이 정상적으로 도구 호출 완료
ErrorEvent

ErrorEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
status.code	Object	-	응답 상태 코드
CLOVA Studio 문제 해결 참조

status.message	Object	-	응답 상태 메시지
CLOVA Studio 문제 해결 참조
SignalEvent

SignalEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
data	String	-	전달할 시그널 데이터 정보
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
id:ef40438b-d49a-4fff-9335-a19e5abfcff1
event:token
data:{"message":{"role":"assistant","content":"","toolCalls":[{"id":"call_zumbHGLfLwV3xn0Rn2gSPqfz","type":"function","function":{"name":"get_weather"}}]},"finishReason":null,"created":1749810707,"seed":1775609431,"usage":null}

id:75cae060-e19b-4a82-9106-81b784dcde51
event:token
data:{"message":{"role":"assistant","content":"","toolCalls":[{"type":"function","function":{"partialJson":"{\""}}]},"finishReason":null,"created":1749810707,"seed":1775609431,"usage":null}

id:d29c7e43-d8ed-43f1-8265-6e5fa91b4b65
event:token
data:{"message":{"role":"assistant","content":"","toolCalls":[{"type":"function","function":{"partialJson":"location"}}]},"finishReason":null,"created":1749810707,"seed":1775609431,"usage":null}

id:700f5c00-07b3-4bcc-892d-00913d22ad9f
event:token
data:{"message":{"role":"assistant","content":"","toolCalls":[{"type":"function","function":{"partialJson":"\":"}}]},"finishReason":null,"created":1749810707,"seed":1775609431,"usage":null}

id:0c3e3439-699d-400a-af23-29a09eab28f3
event:token
data:{"message":{"role":"assistant","content":"","toolCalls":[{"type":"function","function":{"partialJson":" \""}}]},"finishReason":null,"created":1749810707,"seed":1775609431,"usage":null}

id:b7506691-ffb0-4e23-a068-ce50013920de
event:token
data:{"message":{"role":"assistant","content":"","toolCalls":[{"type":"function","function":{"partialJson":"서울"}}]},"finishReason":null,"created":1749810707,"seed":1775609431,"usage":null}

id:7c26e5c8-d75e-4e33-8185-1877c9c2c8d7
event:token
data:{"message":{"role":"assistant","content":"","toolCalls":[{"type":"function","function":{"partialJson":"\","}}]},"finishReason":null,"created":1749810707,"seed":1775609431,"usage":null}

...

id:f32289bd-0b94-4733-9df2-9f1a3eee48a6
event:result
data:{"message":{"role":"assistant","content":"","toolCalls":[{"id":"call_zumbHGLfLwV3xn0Rn2gSPqfz","type":"function","function":{"name":"get_weather","arguments":{"location":"서울","unit":"celsius","date":"2025-06-13"}}}]},"finishReason":"tool_calls","created":1749810707,"seed":1775609431,"usage":{"promptTokens":9,"completionTokens":47,"totalTokens":56}}

Python
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)
동작 방식

요청과 응답을 포함한 Function calling의 동작 방식은 다음과 같습니다.

Step 1. 입력 및 함수 정의 전달 

질의 내용을 입력하고 함수 정의를 전달합니다. 요청 예시는 다음과 같습니다.

cURL
Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v3/chat-completions/{modelName}' \
--header 'Authorization: Bearer <api-key>' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}'
--header 'Content-Type: application/json' \
--data '{
  "messages" : [ {
    "content" : "오늘 서울 날씨 알려줘",
    "role" : "user"
  } ],
  "tools" : [ {
    "function" : {
      "description" : "날씨를 알려줄 수 있는 도구",
      "name" : "get_weather",
      "parameters" : {
        "properties" : {
          "location" : {
            "description" : "서울, 대전, 부산 등의 도시 이름",
            "type" : "string"
          },
          "unit" : {
            "enum" : [ "celsius", "fahrenheit" ],
            "type" : "string"
          },
          "date" : {
            "description" : "2023-08-01 같은 형태의 날짜 문자열. 날씨를 알고 싶은 날짜",
            "type" : "string"
          }
        },
        "required" : [ "location" ],
        "type" : "object"
      }
    }
  }],
  "toolChoice" : "auto"
}'

Shell Session
COPY
Python
Code snippet
import requests

API_KEY = "YOUR_API_KEY"
REQUEST_ID = "YOUR_REQUEST_ID"

url = "https://clovastudio.stream.ntruss.com/v3/chat-completions/{modelName}"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "X-NCP-CLOVASTUDIO-REQUEST-ID": REQUEST_ID,
    "Content-Type": "application/json"
}

data = {
    "messages": [
        {
            "content": "내일 서울 날씨 어때?",
            "role": "user"
        }
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "description": "날씨를 알려줄 수 있는 도구",
                "name": "get_weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "description": "서울, 대전, 부산 등의 도시 이름",
                            "type": "string"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"]
                        },
                        "date": {
                            "description": "2025-03-21 같은 형태의 날짜 문자열. 날씨를 알고 싶은 날짜",
                            "type": "string"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ],
    "toolChoice": "auto"
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result)

Python
COPY
Step 2. 호출할 함수 및 인수 반환 

호출할 함수와 인수 정보가 반환됩니다. 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "message": {
            "role": "assistant",
            "content": "",
            "toolCalls": [
                {
                    "id": "call_s83AKVWrPPI6bCTLl5kFGtyo",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": {
                            "location": "서울",
                            "unit": "celsius",
                            "date": "2025-04-10"
                        }
                    }
                }
            ]
        },
        "finishReason": "tool_calls",
        "created": 1744218663,
        "seed": 1354242582,
        "usage": {
            "promptTokens": 134,
            "completionTokens": 48,
            "totalTokens": 315
        }
    }
}

JSON
COPY
Step 3. 응답 결과 기반으로 실제 함수 호출 

Step 2.의 응답 결과를 기반으로 실제 함수를 호출합니다. 요청 예시는 다음과 같습니다.

cURL
Code snippet
# <예시> 다음과 같은 API를 호출한다고 가정합니다.
# GET https://weather.example.com?location=서울&unit=celsius&date=2025-04-10

curl --request GET 'https://weather.example.com?location=서울&unit=celsius&date=2025-04-10' 

Shell Session
COPY
Python
Code snippet
"""
<예시> 다음과 같은 함수를 구성했다고 가정합니다.
def get_weather(location, unit="celsius", date=None):
    response = requests.get(f"https://weather.example.com?location={location}&unit={unit}&date={date}")
    data = response.json()
    return data
"""

tool_call = result["result"]["message"]["toolCalls"][0]
function_name = tool_call["function"]["name"]
arguments = tool_call["function"]["arguments"]

if function_name == "get_weather":
    function_result = get_weather(**arguments) 

Python
COPY

응답 예시는 다음과 같습니다.

Code snippet
{ "location": "서울", "temperature": "17도", "condition": "맑음" }

JSON
COPY
Step 4. 함수 실행 결과 전달 

함수 실행 결과를 전달합니다. 요청 예시는 다음과 같습니다.

cURL

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v3/chat-completions/{modelName}' \
--header 'Authorization: Bearer <api-key>' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}'
--header 'Content-Type: application/json' \
  --data '{
    "messages": [
      {
        "role": "user",
        "content": "내일 서울 날씨 어때?"
      },
      {
        "role": "assistant",
        "content": "",
        "toolCalls": [
          {
            "id": "call_s83AKVWrPPI6bCTLl5kFGtyo",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": {
                "location": "서울",
                "unit": "celsius",
                "date": "2025-04-10"
              }
            }
          }
        ]
      },
      {
        "role": "tool",
        "toolCallId": "call_s83AKVWrPPI6bCTLl5kFGtyo",
        "content": "{ \"location\": \"서울\", \"temperature\": \"17도\", \"condition\": \"맑음\" }"
      }
    ],
    "seed": 0,
    "topP": 0.8,
    "topK": 0,
    "maxTokens": 1024,
    "temperature": 0,
    "repeatPenalty": 1.1,
    "stopBefore": []
  }'

Shell Session
COPY

Python

Code snippet
url = "https://clovastudio.stream.ntruss.com/v3/chat-completions/{modelName}"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "X-NCP-CLOVASTUDIO-REQUEST-ID": REQUEST_ID,
    "Content-Type": "application/json"
}

data = {
    "messages": [
        {
            "role": "user",
            "content": "내일 서울 날씨 어때?"
        },
        {
            "role": "assistant",
            "content": "",
            "toolCalls": [
                {
                    "id": "call_s83AKVWrPPI6bCTLl5kFGtyo",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": {
                            "location": "서울",
                            "unit": "celsius",
                            "date": "2025-04-10"
                        }
                    }
                }
            ]
        },
        {
            "role": "tool",
            "toolCallId": "call_s83AKVWrPPI6bCTLl5kFGtyo",
            "content": str(function_result)
        }
    ],
    "seed": 0,
    "topP": 0.8,
    "topK": 0,
    "maxTokens": 1024,
    "temperature": 0,
    "repeatPenalty": 1.1,
    "stopBefore": []
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result)

Python
COPY
Step 5. 최종 텍스트 응답 반환 

최종 반환된 응답 결과의 텍스트를 확인합니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "message": {
            "role": "assistant",
            "content": "내일 서울의 날씨는 맑을 예정이며, 기온은 17도로 예상됩니다. 따뜻한 봄날씨가 될 것 같으니 외출하기에 좋은 날이 될 것 같아요!"
        },
        "finishReason": "stop",
        "created": 1744218776,
        "seed": 2744409319,
        "usage": {
            "promptTokens": 88,
            "completionTokens": 37,
            "totalTokens": 125
        }
    }
}

JSON
COPY

---

## Structured Outputs

원문: https://api.ncloud-docs.com/docs/clovastudio-chatcompletionsv3-so

Classic/VPC 환경에서 이용 가능합니다.

Structured Outputs를 지원하여 원하는 JSON Schema 형식의 출력 결과를 생성할 수 있는 v3 Chat Completions에 대해 설명합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v3/chat-completions/{modelName}
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	Enum	Required	모델 이름
<예시> HCX-007
참고

Structured Outputs는 HCX-007 모델에서만 사용할 수 있습니다.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
messages	Array	Required	대화 메시지: messages
topP	Double	Optional	생성 토큰 후보군을 누적 확률을 기반으로 샘플링
0.00 ＜ topP ≤ 1.00 (기본값: 0.80)

topK	Integer	Optional	생성 토큰 후보군에서 확률이 높은 K개를 후보로 지정하여 샘플링
0 ≤ topK ≤ 128 (기본값: 0)

maxCompletionTokens	Integer	Optional	최대 생성 토큰 수
0 ＜ maxCompletionTokens ≤ 32768 (기본값: 512)

temperature	Double	Optional	생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성)
0.00 ≤ temperature ≤ 1.00 (기본값: 0.50)

repetitionPenalty	Double	Optional	같은 토큰을 생성하는 것에 대한 패널티 정도
0.0 ＜ repetitionPenalty ≤ 2.0 (기본값: 1.1)
설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소
1.0~1.1에서 0.05 단위로 미세 조정 권장

stop	Array	Optional	토큰 생성 중단 문자
[](기본값)

seed	Integer	Optional	모델 반복 실행 시 결괏값의 일관성 수준 조정
0: 일관성 수준 랜덤 적용 (기본값)
1 ≤ seed ≤ 4294967295: 일관되게 생성하고자 하는 결괏값의 seed 값 또는 사용자가 지정하고자 하는 seed 값

thinking	Object	Optional	추론 모델 설정 정보
thinking.effort	String	Optional	추론 여부 및 사고 과정 깊이 설정
none (유효 값)
Structured Outputs와 동시 사용 불가

responseFormat	Object	Optional	모델이 출력하는 답변 형식
responseFormat.type	String	Required	답변 형식 타입
json (유효 값)

responseFormat.schema	Object	Required	답변 형식 스키마
답변 형식 타입에 맞는 스키마
JSON Schema(object) (유효 값)
지원하는 JSON Schema 참조

includeAiFilters	Boolean	Optional	AI 필터(생성된 결괏값에 대해 욕설, 비하/차별/혐오, 성희롱/음란 등 카테고리별로 해당하는 정도) 결과 표시 여부
true | false (기본값)
true: 표시
false: 표시 안 함
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
system | user | assistant |
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 사용자의 발화 또는 질문에 대한 답변

content	String	Required	대화 메시지 내용
텍스트 입력(String)
지원하는 JSON Schema

지원하는 JSON Schema에 대한 설명은 다음과 같습니다.

타입
string, number, boolean, integer, object, array
제약 키워드(Validation Keyword)
문자열 (string)
format: 정의된 형식 중 하나여야 함
<예시>
"date-time": "2025-06-30T14:00:00Z",  
"date": "2025-06-30",  
"time": "14:30:00",  
"duration": "P3Y6M4DT12H30M5S",  
"email": "user@example.com",  
"hostname": "example.com",  
"ipv4": "192.***.***.***",  
"ipv6": "2001:****::1",  
"uuid": "123e4567-e89b-12d3-a456-426614174000"

숫자 (number, integer)
minimum: 최소값 (이상)
maximum: 최대값 (이하)
배열 (array)
minItems: 최소 아이템 개수
maxItems: 최대 아이템 개수
items: 배열 항목 스키마 정의
객체 (object)
properties: 필드 스키마 정의
required: 필수 필드 목록
Enum 및 복합 스키마
enum: 미리 정의된 값 목록 중 하나여야 함
anyOf: 나열된 스키마 중 하나 이상을 만족해야 함
참고

일부 필드 입력 시 다음 내용을 확인해 주십시오.

role: system인 대화 메시지는 요청당 1개만 포함할 수 있습니다.
Structured Outputs와 추론 또는 Function calling을 동시에 요청할 수 없습니다.
Structured Outputs는 JSON schema의 일부만 지원합니다.
pattern(Validation Keyword)는 지원하지 않습니다.
요청 예시

요청 예시는 다음과 같습니다.

curl --location --request POST 'https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-007' \
--header 'Authorization: Bearer {CLOVA Studio API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
      {
        "role": "system",
        "content": "- 미리 정의한 JSON Schema 형식에 맞춰 답변하는 AI 어시스턴트입니다."
      },
      {
        "role": "user",
        "content":  "오늘의 최고 기온은 32도, 최저 기온은 15도, 강수 확률은 30%입니다."
      }
    ],
    "topP": 0.8,
    "topK": 0,
    "maxCompletionTokens": 100,
    "temperature": 0.5,
    "repetitionPenalty": 1.1,
    "thinking": {"effort": "none"},
    "stop": [],
    "responseFormat": {
      "type" : "json",
      "schema": {
        "type": "object",
        "properties": {
          "temp_high_c": {
            "type": "number",
            "description": "최고 기온(섭씨)"
          },
          "temp_low_c": {
            "type": "number",
            "description": "최저 기온(섭씨)"
          },
          "precipitation_percent": {
            "type": "number",
            "description": "강수 확률(%)",
            "minimum": 0,
            "maximum": 100
          }
        },
        "required": [
          "temp_high_c",
          "temp_low_c",
          "precipitation_percent"
        ]
      }
    }
  }'

응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.created	Integer	-	응답 날짜
Unix timestamp miliseconds 형식

result.usage	Object	-	토큰 사용량
result.usage.completionTokens	Integer	-	생성 토큰 수
result.usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
result.usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수

result.message	Object	-	대화 메시지
result.message.role	Enum	-	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

result.message.content	String	-	대화 메시지 내용
result.finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현
tool_calls: 모델이 정상적으로 도구 호출 완료

result.seed	Integer	-	입력 seed 값(0 입력 또는 미입력 시 랜덤 값 반환)
result.aiFilter	Array	-	AI 필터 결과: aiFilter
aiFilter

aiFilter에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
groupName	String	-	AI 필터 카테고리
curse | unsafeContents
curse: 비하, 차별, 혐오 및 욕설
unsafeContents: 성희롱, 음란

name	String	-	AI 필터 세부 카테고리
discrimination | insult | sexualHarassment
discrimination: 비하, 차별, 혐오
insult: 욕설
sexualHarassment: 성희롱, 음란

score	String	-	AI 필터 점수
-1 | 0 | 1 | 2
-1: AI 필터 오류 발생
0: 대화 메시지에 민감/위험 표현 포함 가능성 높음
1: 대화 메시지에 민감/위험 표현 포함 가능성 있음
2: 대화 메시지에 민감/위험 표현 포함 가능성 낮음

result	String	-	AI 필터 정상 작동 여부
OK | ERROR
OK: 정상 작동
ERROR: 오류 발생
참고

AI Filter는 최대 500자까지 분석할 수 있습니다. 단, 분석 대상 텍스트에 비정상적인 형식, 이모티콘, 특수 문자 등이 많은 경우, 정상적으로 분석되지 않을 수 있습니다.

응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "message": {
            "role": "assistant",
            "content": "{\n  \"temp_high_c\": 32,\n  \"temp_low_c\": 15,\n  \"precipitation_percent\": 30\n}"
        },
        "finishReason": "stop",
        "created": 1754315742,
        "seed": 965671181,
        "usage": {
            "promptTokens": 39,
            "completionTokens": 31,
            "totalTokens": 70
        },
        "aiFilter": [
            {
                "groupName": "curse",
                "name": "insult",
                "score": "1",
                "result": "OK"
            },
            {
                "groupName": "curse",
                "name": "discrimination",
                "score": "1",
                "result": "OK"
            },
            {
                "groupName": "unsafeContents",
                "name": "sexualHarassment",
                "score": "2",
                "result": "OK"
            }
        ]
    }
}

실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)
응답 스트림

생성되는 토큰을 하나씩 출력하도록 토큰 스트리밍을 사용할 수 있습니다. 토큰 스트리밍 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Accept	-	응답 데이터의 형식
text/event-stream
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

StreamingChatCompletionsTokenEvent

StreamingChatCompletionsTokenEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
created	Integer	-	응답 시간 타임스탬프
usage	Object	-	토큰 사용량
usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
usage.completionTokens	Integer	-	생성 토큰 수
message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현
StreamingChatCompletionsResultEvent

StreamingChatCompletionsResultEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
created	Integer	-	응답 시간 타임스탬프
usage	Object	-	토큰 사용량
usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
usage.completionTokens	Integer	-	생성 토큰 수
usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수

message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
finishReason	String	-	토큰 생성 중단 이유(일반적으로 마지막 이벤트에 전달)
length | stop
length: 길이 제한
stop: 답변 생성 중 stop에 지정한 문자 출현

aiFilter	Array	-	AI 필터 결과: aiFilter
ErrorEvent

ErrorEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
status.code	Object	-	응답 상태 코드
CLOVA Studio 문제 해결 참조

status.message	Object	-	응답 상태 메시지
CLOVA Studio 문제 해결 참조
SignalEvent

SignalEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
data	String	-	전달할 시그널 데이터 정보
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

id: aabdfe-dfgwr-edf-hpqwd-f3asd-g
event: token
data: {"message": {"role": "assistant", "content": "{\n"},"finishReason": null, "created": 1744710905, "seed": 3284419119, "usage": null} 

id: aabdfe-dfgwr-edf-hpqwd-f2asd-g
event: token
data: {"message": {"role": "assistant", "content": " "},"finishReason": null, "created": 1744710905, "seed": 3284419119, "usage": null} 

...

id: aabdfe-dfgwr-edf-hpqwd-f1asd-g
event: result
data: {"message": {"role": "assistant", "content": "{\n  \"temp_high_c\": 32,\n  \"temp_low_c\": 15,\n  \"precipitation_percent\": 30\n}"}, "finishReason": "stop", "created": 1744710905, "seed": 3284419119, "usage": {"promptTokens": 20, "completionTokens": 5, "totalTokens": 25}}

실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

# Chat Completions

## Chat Completions

원문: https://api.ncloud-docs.com/docs/clovastudio-chatcompletions

Classic/VPC 환경에서 이용 가능합니다.

대화형 문장을 생성하는 HCX-003 모델과 경량화된 HCX-DASH-001 모델을 이용할 수 있는 Chat Completions에 대해 설명합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	
/v1/chat-completions/{modelName}
모델을 사용하여 문장 생성
/v1/tasks/{taskId}/chat-completions
/v2/tasks/{taskId}/chat-completions
튜닝 학습한 작업을 사용하여 문장 생성
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	String	Conditional	모델 이름
모델을 사용하여 문장 생성을 하려는 경우
<예시> HCX-003

taskId	String	Conditional	학습 아이디
튜닝 학습한 작업을 사용하여 문장 생성을 하려는 경우
학습 생성 참조
요청 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
messages	Array	Required	대화 메시지: messages
temperature	Double	Optional	생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성)
0.00 ＜ temperature ≤ 1.00 (기본값: 0.50)
소수점 둘째 자리까지 표기

topK	Integer	Optional	생성 토큰 후보군에서 확률이 높은 K개를 후보로 지정하여 샘플링
0 ≤ topK ≤ 128 (기본값: 0)

topP	Double	Optional	생성 토큰 후보군을 누적 확률을 기반으로 샘플링
0.00 ＜ topP ≤ 1.00 (기본값: 0.80)
소수점 둘째 자리까지 표기

repeatPenalty	Double	Optional	같은 토큰을 생성하는 것에 대한 패널티 정도(설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소)
0.0 ＜ repeatPenalty ≤ 10.0 (기본값: 5.0)

stopBefore	Array	Optional	토큰 생성 중단 문자
[](기본값)

maxTokens	Integer	Optional	최대 생성 토큰 수
0 ＜ maxTokens ≤ 4096 (기본값: 100)

includeAiFilters	Boolean	Optional	AI 필터(생성된 결괏값에 대해 욕설, 비하/차별/혐오, 성희롱/음란 등 카테고리별로 해당하는 정도) 결과 표시 여부
false (기본값) | true
false: 표시 안 함
true: 표시

seed	Integer	Optional	모델 반복 실행 시 결괏값의 일관성 수준 조정
0: 일관성 수준 랜덤 적용 (기본값)
1 ≤ seed ≤ 4294967295: 일관되게 생성하고자 하는 결괏값의 seed 값 또는 사용자가 지정하고자 하는 seed 값
참고

일부 필드 입력 시 다음 내용을 확인해 주십시오.

HCX-003
입력 토큰과 출력 토큰의 합은 8,192 토큰을 초과할 수 없습니다.
입력 토큰은 최대 7,600 토큰까지 가능합니다.
모델에 요청할 출력 토큰(maxTokens)은 최대 4,096 토큰까지 가능합니다.
HCX-DASH-001
입력 토큰과 출력 토큰의 합은 4,096 토큰을 초과할 수 없습니다.
입력 토큰은 최대 3,500 토큰까지 가능합니다.
모델에 요청할 출력 토큰(maxTokens)은 최대 4,096 토큰까지 가능합니다.
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 사용자의 발화 또는 질문에 대한 답변

content	String	Required	대화 메시지 내용
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/chat-completions/HCX-003' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--header 'Accept: text/event-stream' \
--data '{
  "topK" : 0,
  "includeAiFilters" : true,
  "maxTokens" : 256,
  "temperature" : 0.5,
  "messages" : [ {
    "role" : "system",
    "content" : "test"
  }, {
    "role" : "user",
    "content" : "테스트 해보자."
  }, {
    "role" : "assistant",
    "content" : "알겠습니다. 무엇을 테스트해볼까요?"
  } ],
  "stopBefore" : [ ],
  "repeatPenalty" : 5.0,
  "topP" : 0.8
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.message	Object	-	대화 메시지
result.message.role	Enum	-	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

result.message.content	String	-	대화 메시지 내용
result.stopReason	Enum	-	결괏값 생성 중단 이유
length | end_token | stop_before
length: 길이 제한
end_token: 토큰 수 제한
stop_before: 모델이 자체적으로 출력을 종료
답변 생성 중 stopBefore에 지정한 문자 출현

result.inputLength	Integer	-	입력 토큰 수(과금 기준으로 end of turn과 같은 특수 토큰도 포함)
result.outputLength	Integer	-	응답 토큰 수
result.seed	int	-	입력 seed 값(0 입력 또는 미입력 시 랜덤 값 반환)
result.aiFilter	Array	-	AI 필터 결과: aiFilter
aiFilter

aiFilter에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
groupName	String	-	AI 필터 카테고리
curse | unsafeContents
curse: 비하, 차별, 혐오 및 욕설
unsafeContents: 성희롱, 음란

name	String	-	AI 필터 세부 카테고리
discrimination | insult | sexualHarassment
discrimination: 비하, 차별, 혐오
insult: 욕설
sexualHarassment: 성희롱, 음란

score	String	-	AI 필터 점수
-1 | 0 | 1 | 2
-1: AI 필터 오류 발생
0: 대화 메시지에 민감/위험 표현 포함 가능성 높음
1: 대화 메시지에 민감/위험 표현 포함 가능성 있음
2: 대화 메시지에 민감/위험 표현 포함 가능성 낮음

result	String	-	AI 필터 정상 작동 여부
OK | ERROR
OK: 정상 작동
ERROR: 오류 발생
참고

AI Filter는 최대 500자까지 분석할 수 있습니다. 단, 분석 대상 텍스트에 비정상적인 형식, 이모티콘, 특수 문자 등이 많은 경우, 정상적으로 분석되지 않을 수 있습니다.

응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
  "status": {
    "code": "20000",
    "message": "OK"
  },
  "result": {
    "message": {
      "role": "assistant",
      "content": "문구: 오늘 하루 있었던 일들을 기록하며, 내일을 준비하세요. 다이어리는 당신의 삶을 더욱 풍요롭게 만들어 줄 것입니다.\n"
    },
    "stopReason": "LENGTH",
    "inputLength": 100,
    "outputLength": 10,
    "aiFilter": [
      {
        "groupName": "curse",
        "name": "insult",
        "score": "1"
      },
      {
        "groupName": "curse",
        "name": "discrimination",
        "score": "0"
      },
      {
        "groupName": "unsafeContents",
        "name": "sexualHarassment",
        "score": "2"
      }
    ]
  }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)
응답 스트림

생성되는 토큰을 하나씩 출력하도록 토큰 스트리밍을 사용할 수 있습니다. 토큰 스트리밍 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Accept	-	응답 데이터의 형식
text/event-stream
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

StreamingChatCompletionsResultEvent

StreamingChatCompletionsResultEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
stopReason	Enum	-	결괏값 생성 중단 이유
length | end_token | stop_before
length: 길이 제한
end_token: 토큰 수 제한
stop_before: 답변 생성 중 stopBefore에 지정한 문자 출현

inputLength	Integer	-	입력 토큰 수(과금 기준으로 end of turn과 같은 특수 토큰도 포함)
outputLength	Integer	-	응답 토큰 수(과금 기준으로 end of turn과 같은 특수 토큰도 포함)
aiFilter	Array	-	AI 필터 결과: aiFilter
StreamingChatCompletionsTokenEvent

StreamingChatCompletionsTokenEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	요청을 식별하는 이벤트 아이디
message	Object	-	대화 메시지
message.role	Enum	-	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

message.content	String	-	대화 메시지 내용
inputLength	Integer	-	입력 토큰 수(과금 기준으로 end of turn과 같은 특수 토큰도 포함)
outputLength	Integer	-	응답 토큰 수(과금 기준으로 end of turn과 같은 특수 토큰도 포함)
stopReason	Enum	-	결괏값 생성 중단 이유
length | end_token | stop_before
length: 길이 제한
end_token: 토큰 수 제한
stop_before:
모델이 정상적으로 생성 완료
답변 생성 중 stopBefore에 지정한 문자 출현
ErrorEvent

ErrorEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
SignalEvent

SignalEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
data	String	-	전달할 시그널 데이터 정보
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
id: aabdfe-dfgwr-edf-hpqwd-f3asd-g
event: token
data: {"message": {"role": "assistant", "content": “안”}}

id: aabdfe-dfgwr-edf-hpqwd-f2asd-g
event: token
data: {"message": {"role": "assistant", "content": “녕”}}

id: aabdfe-dfgwr-edf-hpqwd-f1asd-g
event: result
data: {"message": {"role": "assistant", "content": “안녕”}, "inputLength":20, "outputLength":5, "stopReason":"stop_before" }

Python
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

# 오픈AI 호환성

## 오픈AI 호환성

원문: https://api.ncloud-docs.com/docs/clovastudio-openaicompatibility

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio 서비스는 Chat Completions, 임베딩을 비롯한 주요 API에 대해 오픈AI API와의 호환성을 제공합니다.

호환 API

CLOVA Studio 서비스에서 오픈AI API와 호환되는 API 목록은 다음과 같습니다.

API	메서드	URI
Chat Completions, Chat Completions v3	POST	/chat/completions
임베딩, 임베딩 v2	POST	/embeddings
모델 조회	GET	/models
사용 방법

오픈AI 호환 API의 요청 형식과 응답 형식을 설명합니다.

요청

CLOVA Studio API의 요청 항목을 일부 조정하여 OpenAI 공식 라이브러리(SDK) 및 REST API로 이용할 수 있습니다.

API 키

CLOVA Studio 서비스에서 발급받은 테스트 또는 서비스 API 키를 이용합니다.

주의

오픈AI 호환 API는 CLOVA Studio의 [API 키] 에서 발급받은 테스트 API 키나 서비스 API 키를 통해서만 사용할 수 있습니다.

API URL

요청 API URL은 다음과 같습니다.

https://clovastudio.stream.ntruss.com/v1/openai/

모델

요청 바디의 모델 이름은 CLOVA Studio 서비스에서 제공하는 모델 이름으로 입력해 주십시오.

명명 규칙

요청 필드의 명명 규칙은 스네이크 표기법(snake_case)을 준수합니다.

참고

CLOVA Studio의 Chat Completions (V3 포함), 임베딩 API 필드 명명 규칙이 카멜 표기법(camelCase)을 따르는 것과 상이한 점에 유의하시기 바랍니다. 지원/미지원 필드 목록은 호환 정보를 참고해주세요.

응답

오픈AI API와 동일한 구조와 형식의 응답 결과를 지원합니다.

SDK 예제

OpenAI 공식 라이브러리를 활용하여 CLOVA Studio 서비스를 이용하는 예제를 소개합니다.

Python

Python으로 작성한 예제는 다음과 같습니다.

from openai import OpenAI

client = OpenAI(
    api_key="CLOVA_STUDIO_API_KEY",  # CLOVA Studio API 키
    base_url="https://clovastudio.stream.ntruss.com/v1/openai"  # CLOVA Studio 오픈AI 호환 API URL 
)

# Chat Completions
response = client.chat.completions.create(
    model="HCX-005",  # CLOVA Studio 지원 모델명
    messages=[
        {"role": "system", "content": "당신은 유능한 AI 어시스턴트입니다."},
        {"role": "user", "content": "인공지능에 대해 설명해 주세요."}
    ]
)

print(response.choices[0].message.content)

# Embeddings
embedding = client.embeddings.create(
    model="bge-m3", # CLOVA Studio 지원 모델명 (임베딩)
    input="클로바 스튜디오를 이용해 주셔서 감사합니다.",
    encoding_format="float" # 오픈AI Python SDK로 임베딩을 이용하는 경우, 필수 설정(base64 미지원)
    )
    
print(embedding.data[0].embedding)

유의사항

OpenAI 공식 Python 라이브러리로 임베딩을 이용하고자 하는 경우, encoding_format="float"은 필수 설정입니다.

TypeScript/JavaScript (Node.js)

TypeScript/JavaScript (Node.js)로 작성한 예제는 다음과 같습니다.

import OpenAI from "openai";

const openai = new OpenAI({
    baseURL: "https://clovastudio.stream.ntruss.com/v1/openai", // CLOVA Studio 오픈AI 호환 API URL
    apiKey: "YOUR_API_KEY",
    }); // CLOVA Studio API 키

// Chat Completions
const completion = await openai.chat.completions.create({
    model: "HCX-005",   // CLOVA Studio 지원 모델명
    messages: [
        {"role": "system", "content": "당신은 유능한 AI 어시스턴트입니다."},
        {"role": "user", "content": "인공지능에 대해 설명해 주세요."}
    ]
});

console.log(completion.choices[0].message);

// Embedding
const embedding = await openai.chat.completions.create({
    model: "bge-m3",   // CLOVA Studio 지원 모델명 (임베딩)
    input: "클로바 스튜디오를 이용해주셔서 감사합니다."    
});

console.log(embedding.data[0].embedding);

참고

이외 다양한 언어의 OpenAI 공식 SDK 및 호환 API로 구현된 오픈소스 프레임워크를 통해 CLOVA Studio를 이용할 수 있습니다.

호환 정보 

오픈AI API와 호환되는 API별 상세 호환 정보를 안내합니다. 지원 필드와 CLOVA Studio 전용 필드의 입력 형식 및 범위는 해당 API 가이드를 확인해 주십시오.

Chat Completions/Chat Completions v3

Chat Completions API, Chat Completions v3 API의 오픈AI 호환 정보는 다음과 같습니다.

지원 필드	미지원 필드	CLOVA Studio 전용 필드

messages
messages[].name
model
stream
max_completion_tokens (기본값: 512)
max_tokens (기본값: 512)
n
temperature
tools
tool_choice
parallel_tool_calls
reasoning_effort | reasoning.effort
response_format
top_p
stop
seed
	
audio
frequency_penalty
logit_bias
logprobs
metadata
modalities
prediction
presence_penalty
prompt_cache_key
safety_identifier
service_tier
store
stream_options
top_logprobs
user
web_search_options
	
top_k
repeat_penalty
repetition_penalty
참고

아래 필드는 CLOVA Studio에서 지원하는 범위 내에서 호환성을 제공합니다.

n: 1 (유효값, 기본값)
tool_choice: auto (기본값) | none | object (특정 도구 호출)
parallel_tool_calls: true (유효값, 기본값)
reasoning_effort (또는 reasoning.effort): none | low | medium | high
response_format.type: json_schema (유효값)
response_format.json_schema.name: Optional 지원 (입력값 미인식)
response_format.json_schema.strict: Optional 지원 (입력값 미인식)
임베딩/임베딩 v2 

임베딩 API, 임베딩 v2 API의 오픈AI 호환 정보는 다음과 같습니다.

지원 필드	미지원 필드	CLOVA Studio 전용 필드

input
model
dimensions
encoding_format
	
user
	-
참고

아래 필드는 CLOVA Studio에서 지원하는 범위 내에서 호환성을 제공합니다.

dimensions: 1024 (유효값, 기본값)
encoding_format: float (유효값, 기본값)

---

# 튜닝

## 학습 조회

원문: https://api.ncloud-docs.com/docs/clovastudio-gettask

Classic/VPC 환경에서 이용 가능합니다.

생성한 학습 목록 중 원하는 학습 정보를 조회합니다. 학습별 학습 진행 상태, 현재 스텝 수 등을 확인할 수 있습니다. 학습 조회 API 호출에 필요한 학습 아이디는 학습 생성 API의 응답 바디에서 확인할 수 있습니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
GET	/tuning/v2/tasks/{taskId}
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
taskId	String	Required	학습 아이디
학습 목록 조회 참조
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request GET 'https://clovastudio.stream.ntruss.com/tuning/v2/tasks/{taskId}' \
--header 'Authorization: Bearer {API Key}' \
--header 'Content-Type: application/json' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' 

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.id	String	-	학습 아이디
result.name	String	-	학습 이름
result.model	String	-	튜닝 모델 이름
result.trainEpochs	Integer	-	모델을 학습한 에폭 수
result.learningRate	Double	-	학습률(튜닝 시 모델 파라미터를 재학습하는 수준 및 정도)
result.status	String	-	학습 진행 상태
WAIT | RUNNING | FAILED | SUCCEEDED
WAIT: 학습 대기 중
RUNNING: 학습 중
FAILED: 학습 중단
SUCCEEDED: 학습 완료

result.statusInfo	Array	-	학습 진행 상태 상세 정보: statusInfo
result.createdClientType	String	-	학습을 요청한 클라이언트 유형
API | WEB
API: API 클라이언트
WEB: 웹 클라이언트

result.createdDate	String	-	학습 생성 날짜
ISO 8601 형식

result.updatedDate	String	-	학습 수정 날짜
ISO 8601 형식
statusInfo

statusInfo에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
label	Array	-	
학습 유형이 CLASSIFICATION인 경우: 사용자 데이터 라벨 표시
학습 유형이 GENERATION인 경우: null

dataRows	Integer	-	데이터 수
numOfTokens	Integer	-	데이터 토큰 수
currStep	Integer	-	학습 현재 스텝 수
totalTrainSteps	Integer	-	학습 총 스텝 수
currEpoch	Integer	-	현재 에폭
totalTrainEpochs	Integer	-	전체 학습 에폭
estimatedTime	Integer	-	예상 소요 시간
1 에폭 평균 시간과 전체 학습 에폭 수를 곱해 도출

trainLoss	Double	-	학습 손실량
sendWeightSuccess	Boolean	-	학습 결과 저장 여부
false | true
false: 저장 안 함
true: 저장

failureReason	String	-	학습 실패(FAILED) 이유
message	String	-	학습 실패(FAILED) 이유의 상세 메시지
endDatetime	String	-	학습 종료 날짜
ISO 8601 형식
failureReason, message

학습 실패 이유(failureReason)와 학습 실패 이유의 상세 메시지(message)에 대한 설명은 다음과 같습니다.

학습 실패 이유	상세 메시지	설명
file.extension	Unavailable file extension. Please check the file extension again.	요청한 tuningType에 부합하지 않는 데이터 파일 확장자
file.size	Exceeded the disk usage limit. Please check if the file size is {limit} or less.	학습 요청에서 기대하는 파일 크기 초과
file.encoding	Unsupported charset	UTF8-sig 인코딩이 아닌 경우
file.format	Invalid json format. {reason}	데이터셋 파일(.json/.jsonl)의 디코딩이 불가능한 경우
file.format	Invalid dataset: required field empty. {column}	데이터셋 파일에 필수 column 누락
file.format	Invalid dataset: unexpected column. {column}	데이터셋 파일에 예상 밖의 column 존재
file.format	Invalid dataset: duplicate columns. {column}	데이터셋 파일에 대소문자 구별이 되지 않아 중복되는 column 발생
file.format	Invalid dataset: column order	데이터셋 파일의 column 순서가 System_Prompt, C_ID, T_ID, Text, Completion이 아닌 경우
file.format	Invalid dataset: {column}	데이터셋 파일의 C_ID 또는 T_ID가 0부터 시작해서 1씩 커지는 패턴을 만족하지 않거나 값이 비어 있는 경우
file.error	-	학습 시 파일 읽기 오류
file.noexist	-	데이터셋 파일이 존재하지 않는 경우
File not found	-	Object Storage에서 파일을 찾을 수 없는 경우
resource.timeout	-	GPU 확보 실패로 응답 시간 초과. 다시 시도 필요
clops.error	-	학습 중 CLOps 오류
train.unknown	-	학습 중 파일 관련 외 오류
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
},
"result": {
    "id": "czf9fbky",
    "name": "230821-130704",
    "model": "HCX-003",
    "trainEpochs": 8,
    "learningRate": 1.0E-4,
    "status": "WAIT",
    "statusInfo": {
        "label": null,
        "dataRows": null,
        "numOfTokens": null,
        "currStep": null,
        "totalTrainSteps": null,
        "currEpoch": null,
        "totalTrainEpochs": null,
        "estimatedTime": null,
        "trainLoss": null,
        "sendWeightSuccess": null,
        "failureReason": null,
        "message": null,
        "endDatetime": null
        },
        "createdClientType": "API",
        "createdDate": "2023-08-21T13:07:06+0900",
        "updatedDate": "2023-08-21T13:07:06+0900"
    }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 학습 목록 조회

원문: https://api.ncloud-docs.com/docs/clovastudio-gettasks

Classic/VPC 환경에서 이용 가능합니다.

생성한 학습 목록을 조회합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
GET	/tuning/v2/tasks
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 쿼리 파라미터

요청 쿼리 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
page	Integer	Optional	페이지 번호
0~N (기본값: 0)

size	Integer	Optional	페이지 출력 수
1~100 (기본값: 20)
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request GET 'https://clovastudio.stream.ntruss.com/tuning/v2/tasks?page=0&size=20' \
--header 'Authorization: Bearer {API Key}' \
--header 'Content-Type: application/json' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' 

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참고
result	Object	-	응답 결과
result.totalPages	Integer	-	전체 페이지 수
result.totalElements	Integer	-	전체 데이터 수
result.size	Integer	-	페이지별 데이터 수
result.number	Integer	-	페이지 번호
result.content	Array	-	학습 정보: content
content

content에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	학습 아이디
name	String	-	학습 이름
model	String	-	튜닝 모델 이름
method	Enum	-	튜닝 기법
LoRA

taskType	String	-	학습 유형
GENERATION | CLASSIFICATION
GENERATION: 생성
CLASSIFICATION: 분류

trainEpochs	Integer	-	모델을 학습한 에폭 수
learningRate	Double	-	학습률(튜닝 시 모델 파라미터를 재학습하는 수준 및 정도)
status	Enum	-	학습 진행 상태
WAIT | RUNNING | FAILED | SUCCEEDED
WAIT: 학습 대기 중
RUNNING: 학습 중
FAILED: 학습 중단
SUCCEEDED: 학습 완료

statusInfo	Array	-	학습 진행 상태 상세 정보: statusInfo
createdClientType	String	-	학습을 요청한 클라이언트 유형
API | WEB
API: API 클라이언트
WEB: 웹 클라이언트

createdDate	String	-	학습 생성 날짜
ISO 8601 형식

updatedDate	String	-	학습 수정 날짜
ISO 8601 형식
statusInfo

statusInfo에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
label	Array	-	
학습 유형이 CLASSIFICATION인 경우: 사용자 데이터 라벨 표시
학습 유형이 GENERATION인 경우: null

dataRows	Integer	-	데이터 수
numOfTokens	Integer	-	데이터 토큰 수
currStep	Integer	-	학습 현재 스텝 수
totalTrainSteps	Integer	-	학습 총 스텝 수
currEpoch	Integer	-	현재 에폭
totalTrainEpochs	Integer	-	전체 학습 에폭
estimatedTime	Integer	-	예상 소요 시간
1 에폭 평균 시간과 전체 학습 에폭 수를 곱해 도출

trainLoss	Double	-	학습 손실량
sendWeightSuccess	Boolean	-	학습 결과 저장 여부
false | true
false: 저장 안 함
true: 저장

failureReason	String	-	학습 실패(FAILED) 이유
message	String	-	학습 실패(FAILED) 이유의 상세 메시지
endDatetime	String	-	학습 종료 날짜 (ISO 8601 형식)
failureReason, message

학습 실패 이유(failureReason)와 학습 실패 이유의 상세 메시지(message)에 대한 설명은 다음과 같습니다.

학습 실패 이유	상세 메시지	설명
file.extension	Unavailable file extension. Please check the file extension again.	요청한 tuningType에 부합하지 않는 데이터 파일 확장자
file.size	Exceeded the disk usage limit. Please check if the file size is {limit} or less.	학습 요청에서 기대하는 파일 크기 초과
file.encoding	Unsupported charset	UTF8-sig 인코딩이 아닌 경우
file.format	Invalid json format. {reason}	데이터셋 파일(.json/.jsonl)의 디코딩이 불가능한 경우
file.format	Invalid dataset: required field empty. {column}	데이터셋 파일에 필수 column 누락
file.format	Invalid dataset: unexpected column. {column}	데이터셋 파일에 예상 밖의 column 존재
file.format	Invalid dataset: duplicate columns. {column}	데이터셋 파일에 대소문자 구별이 되지 않아 중복되는 column 발생
file.format	Invalid dataset: column order	데이터셋 파일의 column 순서가 System_Prompt, C_ID, T_ID, Text, Completion이 아닌 경우
file.format	Invalid dataset: {column}	데이터셋 파일의 C_ID 또는 T_ID가 0부터 시작해서 1씩 커지는 패턴을 만족하지 않거나 값이 비어 있는 경우
file.error	-	파일 읽기 오류
resource.timeout	-	GPU 확보 실패로 응답 시간 초과. 다시 시도 필요
clops.error	-	학습 중 CLOps 오류
train.unknown	-	학습 중 파일 관련 외 오류
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "totalPages": "7,",
        "totalElements": "122,",
        "size": "20,",
        "number": "0,",
        "content": [
        {
            "id": "oi55o2ej",
            "name": "230709-202307",
            "model": "HCX-003",
            "method": "LoRA",
            "taskType": "GENERATION",
            "trainEpochs": 4,
            "learningRate": 1.0E-4,
            "status": "FAILED",
            "statusInfo": {
            "label": null,
            "dataRows": null,
            "numOfTokens": null,
            "currStep": null,
            "totalTrainSteps": null,
            "currEpoch": null,
            "totalTrainEpochs": null,
            "estimatedTime": null,
            "trainLoss": null,
            "sendWeightSuccess": null,
            "failureReason": "resource.timeout"
            },
            "createdClientType": "WEB",
            "createdDate": "2023-08-20T20:23:08+0900",
            "updatedDate": "2023-08-21T10:31:40+0900"
            },
            {
                "id": "oi55o2ej",
                "name": "230709-202307",
                "model": "HCX-002",
                "method": "LoRA",
                "taskType": "GENERATION",
                "trainEpochs": 4,
                "learningRate": 1.0E-4,
                "status": "FAILED",
                "statusInfo": {
                22
                "label": null,
                "dataRows": null,
                "numOfTokens": null,
                "currStep": null,
                "totalTrainSteps": null,
                "currEpoch": null,
                "totalTrainEpochs": null,
                "estimatedTime": null,
                "trainLoss": null,
                "sendWeightSuccess": null,
                "failureReason": "resource.timeout",
                "message": null
                },
                "createdClientType": "WEB",
                "createdDate": "2023-08-21T20:23:08+0900",
                "updatedDate": "2023-08-22T10:31:40+0900"
            }
        ]
    }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 학습 생성

원문: https://api.ncloud-docs.com/docs/clovastudio-posttask

Classic/VPC 환경에서 이용 가능합니다.

학습을 생성합니다. 생성한 학습이 완료된 후 대화형 문장을 생성하는 Chat Completions API, Chat Completions V3 API를 호출하여 CLOVA Studio가 생성한 답변을 확인할 수 있습니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/tuning/v2/tasks
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
name	String	Optional	학습 이름
미 입력 시 학습 생성 날짜로 자동 생성

model	String	Required	튜닝에 사용할 모델 이름
tuningType	String	Optional	튜닝 기법
PEFT (기본값)

trainEpochs	String	Optional	모델을 학습한 에폭 수
1 ≤ trainEpochs ≤ 20 (기본값: 8)

learningRate	String	Optional	학습률(튜닝 시 모델 파라미터를 재학습하는 수준 및 정도)
1 ≤ learningRate ≤ 1.0E-6 (기본값: 1.0E-4)

validationSplitRatio	Double	Optional	검증에 사용할 데이터셋 비율
0.0~0.1 (기본값: 0.0)

loraR	Integer	Optional	PEFT 학습 시 사용할 저차원 행렬의 차원 수
2~64 (기본값: 8)

loraAlpha	Integer	Optional	PEFT 학습 결과 반영 시 적용할 스케일 계수
2~512 (기본값: 64)

trainingDatasetFilePath	String	Conditional	학습할 데이터셋 파일 경로 (버킷명을 제외한 버킷 내 경로)
Object Storage 서비스에 업로드한 경우 필수 입력

trainingDatasetBucket	String	Conditional	학습할 데이터셋 파일을 업로드한 버킷 이름
trainingDatasetFilePath 입력한 경우 필수 입력

trainingDatasetAccessKey	String	Conditional	학습할 데이터셋 파일 접근을 위한 Access key
trainingDatasetFilePath 입력한 경우 필수 입력

trainingDatasetSecretKey	String	Conditional	학습할 데이터셋 파일 접근을 위한 Secret key
trainingDatasetFilePath 입력한 경우 필수 입력
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/tuning/v2/tasks' \
--header 'Authorization: Bearer {API Key}' \
--header 'Content-Type: multipart/form-data' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' 
--data '{
  "name": "generation_task",
  "model": "HCX-003",
  "tuningType": "PEFT",
  "trainEpochs": 8,
  "learningRate": 1e-5f,
  "trainingDatasetFilePath": "root_path/sub_path/file_name",
  "trainingDatasetBucket": "bucket_name",
  "trainingDatasetAccessKey": "access_key",
  "trainingDatasetSecretKey": "secret_key",
   "validationSplitRatio": 0,
   "loraR": 8,
   "loraAlpha": 64
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참고
result	Object	-	응답 결과
result.id	String	-	학습 아이디
result.name	String	-	학습 이름
result.model	String	-	튜닝 모델 이름
result.taskType	String	-	작업 유형
GENERATION: 생성 (기본값)
CLASSIFICATION: 분류

result.trainEpochs	Integer	-	모델을 학습한 에폭 수
result.learningRate	Double	-	학습률(튜닝 시 모델 파라미터를 재학습하는 수준 및 정도)
result.status	String	-	학습 진행 상태
WAIT | RUNNING | FAILED | SUCCEEDED
WAIT: 학습 대기 중
RUNNING: 학습 중
FAILED: 학습 중단
SUCCEEDED: 학습 완료

result.statusInfo	Array	-	학습 진행 상태의 상세 정보: statusInfo
result.createdClientType	String	-	학습을 요청한 클라이언트 유형
API | WEB
API: API 클라이언트
WEB: 웹 클라이언트

result.createdDate	String	-	학습 생성 날짜
ISO 8601 형식

result.updatedDate	String	-	학습 수정 날짜
ISO 8601 형식
statusInfo

statusInfo에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
label	Array	-	
학습 유형이 CLASSIFICATION인 경우: 사용자 데이터 라벨 표시
학습 유형이 GENERATION인 경우: null

dataRows	Integer	-	데이터 수
numOfTokens	Integer	-	데이터 토큰 수
currStep	Integer	-	학습 현재 스텝 수
totalTrainSteps	Integer	-	학습 총 스텝 수
currEpoch	Integer	-	현재 에폭
totalTrainEpochs	Integer	-	전체 학습 에폭
estimatedTime	Integer	-	예상 소요 시간
1 에폭 평균 시간과 전체 학습 에폭 수를 곱해 도출

trainLoss	Double	-	학습 손실량
sendWeightSuccess	Boolean	-	학습 결과 저장 여부
false | true
false: 저장 안 함
true: 저장

failureReason	String	-	학습 실패(FAILED) 이유
message	String	-	학습 실패(FAILED) 이유의 상세 메시지
endDatetime	String	-	학습 종료 날짜
ISO 8601 형식
failureReason, message

학습 실패 이유(failureReason)와 학습 실패 이유의 상세 메시지(message)에 대한 설명은 다음과 같습니다.

학습 실패 이유	상세 메시지	설명
file.extension	Unavailable file extension. Please check the file extension again.	요청한 tuningType에 부합하지 않는 데이터 파일 확장자
file.size	Exceeded the disk usage limit. Please check if the file size is {limit} or less.	학습 요청에서 기대하는 파일 크기 초과
file.encoding	Unsupported charset	UTF8-sig 인코딩이 아닌 경우
file.format	Invalid json format. {reason}	데이터셋 파일(.json/.jsonl)의 디코딩이 불가능한 경우
file.format	Invalid dataset: required field empty. {column}	데이터셋 파일에 필수 column 누락
file.format	Invalid dataset: unexpected column. {column}	데이터셋 파일에 예상 밖의 column 존재
file.format	Invalid dataset: duplicate columns. {column}	데이터셋 파일에 대소문자 구별이 되지 않아 중복되는 column 발생
file.format	Invalid dataset: column order	데이터셋 파일의 column 순서가 System_Prompt, C_ID, T_ID, Text, Completion이 아닌 경우
file.format	Invalid dataset: {column}	데이터셋 파일의 C_ID 또는 T_ID가 0부터 시작해서 1씩 커지는 패턴을 만족하지 않거나 값이 비어 있는 경우
file.error	-	학습 시 파일 읽기 오류
file.noexist	-	데이터셋 파일이 존재하지 않는 경우
File not found	-	Object Storage에서 파일을 찾을 수 없는 경우
resource.timeout	-	GPU 확보 실패로 응답 시간 초과. 다시 시도 필요
clops.error	-	학습 중 CLOps 오류
train.unknown	-	학습 중 파일 관련 외 오류
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
"result": {
    "id": "czf9fbky",
    "name": "230821-130704",
    "model": "HCX-003",
    "trainEpochs": 8,
    "learningRate": 1.0E-4,
    "status": "WAIT",
    "statusInfo": {
        "label": null,
        "dataRows": null,
        "numOfTokens": null,
        "currStep": null,
        "totalTrainSteps": null,
        "currEpoch": null,
        "totalTrainEpochs": null,
        "estimatedTime": null,
        "trainLoss": null,
        "sendWeightSuccess": null,
        "failureReason": null,
        "message":null,
        "endDatetime": null
        },
        "createdClientType": "API",
        "createdDate": "2023-08-21T13:07:06+0900",
        "updatedDate": "2023-08-21T13:07:06+0900"
    }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 학습 삭제

원문: https://api.ncloud-docs.com/docs/clovastudio-deletetask

Classic/VPC 환경에서 이용 가능합니다.

학습을 삭제합니다. 처음 의도했던 결괏값에 좀 더 수렴하는 결과를 얻기 위해 새로운 학습을 진행하고 싶거나 기존의 학습이 더 이상 필요 없는 경우에 사용할 수 있습니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
DELETE	/v2/tasks/{taskId}
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
taskId	String	Required	학습 아이디
학습 목록 조회 참조
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request DELETE 'https://clovastudio.stream.ntruss.com/tuning/v2/tasks/{taskId}' \
--header 'Authorization: Bearer {API Key}' \
--header 'Content-Type: application/json' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' 

Shell Session
COPY
응답

​응답 형식을 설명합니다.

응답 헤더

​응답 헤더에 대한 설명은 다음과 같습니다.

필드	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참고
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
  "status": {
    "code": "20000",
    "message": "OK"
  }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

# 익스플로러

## 리랭커

원문: https://api.ncloud-docs.com/docs/clovastudio-reranker

Classic/VPC 환경에서 이용 가능합니다.

검색한 문서와 사용자 쿼리 간 연관도를 평가하여 관련성 높은 문서들을 선택하고, 그 결과를 요약 및 압축하여 RAG 답변을 생성합니다. 전체 검색 문서가 아닌 사용자 쿼리와 연관도가 높은 문서만 선별하여 사용하기 때문에 토큰 소비를 효율적으로 절감하면서도 신뢰도 높은 결괏값을 얻을 수 있습니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/reranker
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
documents	List[Object]	Required	검색한 문서 목록: documents
query	String	Required	사용자 쿼리
maxTokens	Integer	Optional	최대 생성 토큰 수
maxTokens ＜ 4096 (기본값: 1024)
documents

documents에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	Required	검색한 문서 아이디
doc	String	Required	검색한 문서 원본
참고

리랭커 API의 최대 입력 토큰 수는 128,000이며, 최대 출력 토큰 수는 4,096입니다.

요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/reranker' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
    "documents": [
        {
            "id": "id1",
            "doc": "VPC 삭제 오류 VPC가 삭제되지 않습니다.VPC 삭제 시 \"Endpoint가 전부 반납되지 않아 삭제가 불가능합니다. \"라는 메시지가 나타납니다.원인VPC 하위에 리소스가 존재할 경우, VPC를 삭제할 수 없습니다.해결 방법삭제하려 VPC와 관련된 모든 리소스를 반납하거나 삭제해야 합니다.** 삭제하려는 VPC와 관련된 Server, Network Interface, Cloud functions, Load Balancer, Auto Scaling, NAT Gateway 내 모든 리소스를 삭제해 주십시오.** 해당 VPC와 관련된 Route Table을 삭제해 주십시오.** 해당 VPC와 관련된 Subnet을 삭제해 주십시오.** 서버 eth0에 할당된 Network Interface는 반납 및 삭제할 수 없습니다. 서버 eth0에 할당된 Network Interface를 삭제하려면 해당 서버를 먼저 반납해 주십시오."
        },
        {
            "id": "id2",
            "doc": "VPC 삭제 생성하여 운영 중인 VPC를 삭제할 수 있습니다. 삭제하는 방법은 다음과 같습니다.참고VPC 안에 리소스가 남아 있으면 삭제되지 않습니다.VPC 삭제 시 해당 VPC와 연관된 서비스도 함께 삭제되며, 삭제 후에는 복구가 불가능합니다.** 네이버 클라우드 플랫폼 콘솔의 VPC 환경에서 Services > Networking > VPC 메뉴를 차례대로 클릭해 주십시오.** VPC Management 메뉴를 클릭해 주십시오.** 삭제할 VPC를 클릭한 후 [삭제] 버튼을 클릭해 주십시오.** VPC 삭제 팝업 창이 나타나면 [예] 버튼을 클릭해 주십시오.** VPC Management 화면의 VPC 목록에서 VPC 상태를 확인해 주십시오. 종료중 : VPC를 삭제하고 있는 상태*** 종료중 : VPC를 삭제하고 있는 상태"
        },
        {
            "id": "id3",
            "doc": "Subnet 삭제 생성하여 운영 중인 Subnet을 삭제할 수 있습니다. 삭제하는 방법은 다음과 같습니다.참고Subnet 안에 서버가 있으면 삭제되지 않습니다.한 번 삭제된 Subnet은 복구가 불가능합니다.** 네이버 클라우드 플랫폼 콘솔의 VPC 환경에서 Services > Networking > VPC 메뉴를 차례대로 클릭해 주십시오.** Subnet Management 메뉴를 클릭해 주십시오.** 삭제할 Subnet을 클릭한 후 [Subnet 삭제] 버튼을 클릭해 주십시오.** Subnet 삭제 팝업 창이 나타나면 [예] 버튼을 클릭해 주십시오.** Subnet Management 화면의 Subnet 목록에서 Subnet 상태를 확인해 주십시오. 종료중 : Subnet을 삭제하고 있는 상태*** 종료중 : Subnet을 삭제하고 있는 상태"
        }
    ],
    "query": "VPC 삭제 방법 알려줘"
   ]
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.result	String	-	모델 출력 답변
result.citedDocuments	Array[Object]	-	검색한 문서 중 인용한 문서 목록: citedDocuments
result.suggestedQueries	Array[String]	-	재검색 시 추천 검색어 목록
리랭커 모델이 검색한 문서 중 답변을 찾지 못한 경우에 표시

result.usage	Object	-	토큰 사용량
result.usage.completionTokens	Integer	-	생성 토큰 수
result.usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
result.usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수
citedDocuments

citedDocuments에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	인용한 문서 아이디
doc	String	-	인용한 문서 원본
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

검색한 문서에서 답변을 찾은 경우
Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "result": "답변: VPC를 삭제하려면 먼저 <doc1>VPC와 관련된 모든 리소스를 반납하거나 삭제</doc1>해야 합니다. 여기에는 <doc1>Server, Network Interface, Cloud functions, Load Balancer, Auto Scaling, NAT Gateway 내 모든 리소스</doc1>와 <doc1>Route Table, Subnet</doc1>이 포함됩니다. 특히, <doc1>서버 eth0에 할당된 Network Interface는 반납 및 삭제할 수 없으므로 해당 서버를 먼저 반납해야 합니다.</doc1>\n\n삭제 절차는 다음과 같습니다:\n1. <doc2>네이버 클라우드 플랫폼 콘솔의 VPC 환경에서 Services > Networking > VPC 메뉴를 클릭합니다.</doc2>\n2. <doc2>VPC Management 메뉴를 클릭한 후, 삭제할 VPC를 선택하고 [삭제] 버튼을 클릭합니다.</doc2>\n3. <doc2>VPC 삭제 팝업 창에서 [예] 버튼을 클릭하여 삭제를 진행합니다.</doc2>\n4. <doc2>VPC Management 화면에서 VPC 상태를 확인하여 삭제가 완료되었는지 확인합니다.</doc2>\n\n이 과정을 통해 VPC를 안전하게 삭제할 수 있습니다. 단, <doc2>VPC 삭제 후에는 복구가 불가능하므로 신중하게 진행해야 합니다.</doc2>",
        "citedDocuments": [
            {
                "id": "id1",
                "doc": "VPC 삭제 오류 VPC가 삭제되지 않습니다.VPC 삭제 시 \"Endpoint가 전부 반납되지 않아 삭제가 불가능합니다. \"라는 메시지가 나타납니다.원인VPC 하위에 리소스가 존재할 경우, VPC를 삭제할 수 없습니다.해결 방법삭제하려 VPC와 관련된 모든 리소스를 반납하거나 삭제해야 합니다.** 삭제하려는 VPC와 관련된 Server, Network Interface, Cloud functions, Load Balancer, Auto Scaling, NAT Gateway 내 모든 리소스를 삭제해 주십시오.** 해당 VPC와 관련된 Route Table을 삭제해 주십시오.** 해당 VPC와 관련된 Subnet을 삭제해 주십시오.** 서버 eth0에 할당된 Network Interface는 반납 및 삭제할 수 없습니다. 서버 eth0에 할당된 Network Interface를 삭제하려면 해당 서버를 먼저 반납해 주십시오."
            },
            {
                "id": "id2",
                "doc": "VPC 삭제 생성하여 운영 중인 VPC를 삭제할 수 있습니다. 삭제하는 방법은 다음과 같습니다.참고VPC 안에 리소스가 남아 있으면 삭제되지 않습니다.VPC 삭제 시 해당 VPC와 연관된 서비스도 함께 삭제되며, 삭제 후에는 복구가 불가능합니다.** 네이버 클라우드 플랫폼 콘솔의 VPC 환경에서 Services > Networking > VPC 메뉴를 차례대로 클릭해 주십시오.** VPC Management 메뉴를 클릭해 주십시오.** 삭제할 VPC를 클릭한 후 [삭제] 버튼을 클릭해 주십시오.** VPC 삭제 팝업 창이 나타나면 [예] 버튼을 클릭해 주십시오.** VPC Management 화면의 VPC 목록에서 VPC 상태를 확인해 주십시오. 종료중 : VPC를 삭제하고 있는 상태*** 종료중 : VPC를 삭제하고 있는 상태"
            }
        ],
        "suggestedQueries": [],
        "usage": {
            "promptTokens": 777,
            "completionTokens": 281,
            "totalTokens": 1058
        }
    }
}

JSON
COPY
검색한 문서에서 답변을 찾지 못한 경우
Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "result": "답변: 검색 결과에는 날씨에 대한 정보가 제공되지 않아, 날씨에 대한 정보를 알려드릴 수 없습니다.",
        "citedDocuments": [],
        "suggestedQueries": [
            "현재 날씨 상태",
            "일기 예보"
        ],
        "usage": {
            "promptTokens": 774,
            "completionTokens": 57,
            "totalTokens": 831
        }
    }

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## RAG Reasoning

원문: https://api.ncloud-docs.com/docs/clovastudio-ragreasoning

Classic/VPC 환경에서 이용 가능합니다.

신뢰도를 높이는 인용 출처, 인용 출처 인덱싱 표기 등의 답변 유형에 맞춰 학습한 RAG Reasoning 모델을 활용하여 근거 기반의 RAG 답변 생성합니다. RAG Reasoning은 Function calling 형식으로 엔진을 호출합니다. 단일 혹은 여러 개의 RAG 함수를 지정할 수 있으며, LLM이 상황에 맞게 자율적으로 최적의 함수를 선택하여 검색 증강 생성 작업을 수행할 수 있습니다. 리랭커와 체이닝하여 사용하는 경우, 좀 더 안정적인 결괏값을 얻을 수 있습니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/rag-reasoning
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
messages	Array	Required	대화 메시지: messages
topP	Double	Optional	생성 토큰 후보군을 누적 확률을 기반으로 샘플링
0.00 ＜ topP ≤ 1.00 (기본값: 0.8)

topK	Integer	Optional	생성 토큰 후보군에서 확률이 높은 K개를 후보로 지정하여 샘플링
0 ≤ topK ≤ 128 (기본값: 0)

maxTokens	Integer	Optional	최대 생성 토큰 수
1024 ≤ maxTokens ＜ 4096 (기본값: 1024)

temperature	Double	Optional	생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성)
0.00 ＜ temperature ≤ 1.00 (기본값: 0.50)

repetitionPenalty	Double	Optional	같은 토큰을 생성하는 것에 대한 패널티 정도(설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소)
0.0 ＜ repetitionPenalty ≤ 2.0 (기본값: 1.1)

stop	Array	Optional	토큰 생성 중단 문자
[](기본값)

seed	Integer	Optional	모델 반복 실행 시 결괏값의 일관성 수준 조정
0: 일관성 수준 랜덤 적용 (기본값)
1 ≤ seed ≤ 4294967295: 일관되게 생성하고자 하는 결괏값의 seed 값 또는 사용자가 지정하고자 하는 seed 값

includeAiFilters	Boolean	Optional	AI 필터(생성된 결괏값에 대해 욕설, 비하/차별/혐오, 성희롱/음란 등 카테고리별로 해당하는 정도) 결과 표시 여부
true (기본값) | false
true: 표시
false: 표시 안 함

tools	Array	Required	Function calling 사용 가능 도구 목록: tools
toolChoice	String | Object	Optional	Function calling 도구 호출 동작 방식
auto : 모델이 도구 자동 호출(String)
none : 모델이 도구 호출 없이 일반 답변 생성(String)
모델이 특정도구 강제 호출(Object)

toolChoice.type	String	Optional	Function calling 모델이 호출할 도구 유형
toolChoice.function	Object	Optional	Function calling 모델이 호출할 도구
function(유효 값)

toolChoice.function.name	String	Optional	Function calling 모델이 호출할 도구 이름
참고

RAG Reasoning 의 최대 입력 토큰 수는 128,000이며, 최대 출력 토큰 수는 4,096입니다.

messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
system | user | assistant | tool
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 사용자의 발화 또는 질문에 대한 답변
tool: assistant(모델)가 호출한 함수의 실행 결과

content	String	Required	대화 메시지 내용
텍스트 입력(String)

toolCalls	Array	Conditional	assistant의 호출 도구 정보
role이 tool인 경우, assistant의 toolCalls 요청과 같이 입력

toolCallId	String	Conditional	도구 아이디
role이 tool인 경우, 필수 입력
assistant의 toolCalls 요청과 연결하는 용도
참고

role이 tool인 경우, messages의 content에는 검색 데이터베이스 또는 검색 API에서 검색한 문서 목록(search_result)를 추가해야 합니다. 검색 결과(search_result)에 id: {문서 고유 아이디}, doc: {검색한 문서 원본}을 포함하여 RAG 답변의 인용 표기에 활용될 수 있도록 구성해 주십시오. 예시는 다음과 같습니다.

{
    "role": "tool",
    "content": "[
                    {
                        \"search_result\": [{\"id\": \"doc-1493058999\",
                        \"doc\": \"네이버 계정으로 로그인은 개인 회원만 가능하며 사업자 회원은 불가능합니다.\"
                    },
                    ...
                 ]"
}

tools

tools에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
type	String	Required	도구 유형
function(유효 값)

function	Object	Required	호출 function 정보
function.name	String	Required	function 이름
function.description	String	Required	function 설명
function.parameters	Object	Required	function 사용 시 전달되는 매개변수
properties, required
입력: 동작 방식 참조
형식: JSON Schema reference 참조
toolCalls

toolCalls에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	도구 식별자
type	String	-	도구 유형
function(유효 값)

function	Object	-	호출 function 정보
function.name	String	-	function 이름
function.arguments	Object	-	function 사용 시 전달되는 매개변수
요청 예시

요청 예시는 다음과 같습니다.

Step 1. role: user에 질의 내용을 입력하고 답변 생성에 가장 적합한 함수를 호출 (응답 확인)
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/rag-reasoning' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data-raw '{
  "messages": [
    {
      "content": "A100 GPU 빌리는 방법",
      "role": "user"
    }
  ],
  "tools": [
    {
      "function": {
        "description": "NCloud 관련 검색을 할 때 사용하는 도구입니다.\n나누어 질문해야 하는 경우 쿼리를 쪼개 나누어서 도구를 사용합니다.\n정보를 찾을 수 없었던 경우, 최종 답을 하지 않고 suggested_queries를 참고하여 도구를 다시 사용할 수 있습니다.",
        "name": "ncloud_cs_retrieval",
        "parameters": {
          "properties": {
            "query": {
              "description": "사용자의 검색어를 정제해서 넣으세요.",
              "type": "string"
            }
          },
          "required": [
            "query"
          ],
          "type": "object"
        }
      },
      "type": "function"
    }
  ],
  "toolChoice": "auto",
  "maxTokens": 1024
}'

Step 2. 최종 답변을 생성하기 위한 role: tool을 포함한 요청 (응답 확인)
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/rag-reasoning' \
--header 'Authorization: Bearer <access_token>' \
--header 'Content-Type: application/json' \
--data-raw '{
    "messages": [
        {
            "content": "A100 GPU 빌리는 방법",
            "role": "user"
        },
        {
            "role": "assistant",
            "content": "",
            "toolCalls": [
                {
                    "id": "call_enTEYb0kWBjOwtkngbl7FGTm",
                    "type": "function",
                    "function": {
                        "name": "ncloud_cs_retrieval",
                        "arguments": {
                            "query": "A100 GPU 빌리는 방법"
                        }
                    }
                }
            ]
        },
        {
            "content": "{\"search_result\": [{\"id\": \"doc-179\", \"doc\": \"GPU A100은 KR-1에서만 생성 가능합니다. A100 생성 시에는 KR-1의 Subnet을 선택하여 주시기 바랍니다. GPU 서버는 기업 회원에 한하여 최대 5대까지 생성할 수 있습니다.\"}, {\"id\": \"doc-248\", \"doc\": \"네이버 클라우드 플랫폼 콘솔의 Services > Compute > Server 메뉴에서 GPU A100 서버를 생성할 수 있습니다. 자세한 생성 방법은 서버 생성 가이드를 참고해 주십시오.\"}, {\"id\": \"doc-156\", \"doc\": \"더 많은 GPU 서버가 필요하거나 GPU 서버 생성이 필요한 개인 회원의 경우 FAQ를 참고하여 고객 지원으로 문의해 주십시오.\"}]}",
            "role": "tool",
            "toolCallId": "call_enTEYb0kWBjOwtkngbl7FGTm"
        }
    ],
    "tools": [
        {
            "function": {
                "description": "NCloud 관련 검색을 할 때 사용하는 도구입니다.\n나누어 질문해야 하는 경우 쿼리를 쪼개 나누어서 도구를 사용합니다.\n정보를 찾을 수 없었던 경우, 최종 답을 하지 않고 suggested_queries를 참고하여 도구를 다시 사용할 수 있습니다.",
                "name": "ncloud_cs_retrieval",
                "parameters": {
                    "properties": {
                        "query": {
                            "description": "사용자의 검색어를 정제해서 넣으세요.",
                            "type": "string"
                        }
                    },
                    "required": [
                        "query"
                    ],
                    "type": "object"
                }
            },
            "type": "function"
        }
    ]
}'

응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.message	ChatMessage	-	대화 메시지 목록
result.message.role	Enum	-	대화 메시지 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

result.message.content	String	-	대화 메시지 내용
result.message.thinkingContent	String	-	모델의 의사 결정 흐름
result.message.toolCalls	Array	-	toolCalls
result.usage	Object	-	토큰 사용량
result.usage.completionTokens	Integer	-	생성 토큰 수
result.usage.promptTokens	Integer	-	입력(프롬프트) 토큰 수
result.usage.totalTokens	Integer	-	전체 토큰 수
생성 토큰 수+입력 토큰 수
toolCalls

toolCalls에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	도구 식별자
type	String	-	도구 유형
function(유효값)

function	Object	-	호출 function 정보
function.name	String	-	function 이름
function.arguments	Object	-	function 사용 시 전달되는 매개변수
응답 예시

응답 예시는 다음과 같습니다.

Step 1.에 대한 응답 예시 (요청 확인)

{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "message": {
            "role": "assistant",
            "content": "",
            "thinkingContent": "사용자가 \"A100 GPU 빌리는 방법\"에 대해 문의했습니다. 이 질문에 대한 답변을 찾기 위해 'ncloud_cs_retrieval' 도구를 사용하여 관련 정보를 검색할 필요가 있습니다.",
            "toolCalls": [
                {
                    "id": "call_enTEYb0kWBjOwtkngbl7FGTm",
                    "type": "function",
                    "function": {
                        "name": "ncloud_cs_retrieval",
                        "arguments": {
                            "query": "A100 GPU 빌리는 방법"
                        }
                    }
                }
            ]
        },
        "usage": {
            "promptTokens": 135,
            "completionTokens": 84,
            "totalTokens": 219
        }
    }
}

Step 2.에 대한 응답 예시 (LLM의 최종 답변 반환) (요청 확인)

{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "message": {
            "role": "assistant",
            "content": "A100 GPU를 빌리는 방법은 <doc-248>네이버 클라우드 플랫폼 콘솔의 Services > Compute > Server 메뉴에서 GPU A100 서버를 생성할 수 있습니다.</doc-248> 그러나 <doc-179>GPU A100은 KR-1에서만 생성 가능하며, A100 생성 시에는 KR-1의 Subnet을 선택해야 합니다.</doc-179> 또한, <doc-179>GPU 서버는 기업 회원에 한하여 최대 5대까지 생성할 수 있습니다.</doc-179> 만약 더 많은 GPU 서버가 필요하거나 GPU 서버 생성이 필요한 개인 회원의 경우, <doc-156>FAQ를 참고하여 고객 지원으로 문의해 주십시오.</doc-156>"
        },
        "usage": {
            "promptTokens": 332,
            "completionTokens": 146,
            "totalTokens": 478
        }
    }
}

실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 토큰 계산기(챗)

원문: https://api.ncloud-docs.com/docs/clovastudio-tokenizerhcx

Classic/VPC 환경에서 이용 가능합니다.

HCX 모델에서 입력한 문장의 토큰 수를 계산합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/chat-tokenize/{modelName}
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	String	Required	모델 이름
<예시> HCX-003
요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
messages	Array	Required	토큰 수를 계산할 대화 메시지 목록: messages
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지의 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

content	String	Required	대화 메시지 내용
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/chat-tokenize/{modelName}' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
        "messages": [
        {
            "role": "system",
            "content": "- HyperCLOVA X는 네이버의 하이퍼스케일 AI입니다."
        },
        {
            "role": "user",
            "content": "안녕하세요, 이름이 무엇입니까?"
        },
        {
            "role": "assistant",
            "content": "저는 HyperCLOVA X입니다."
        }
    ]
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.messages	Array	-	토큰 수가 계산된 요청 대화 메시지 목록: messages
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	-	대화 메시지의 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

content	String	-	대화 메시지 내용
count	Integer	-	대화 메시지 토큰 수 계산 결과
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
      "code": "20000",
      "message": "OK"
    },
    "result": {
      "messages": [
        {
          "role": "system",
          "content": "- HyperCLOVA X 는 네이버의 하이퍼스케일 AI 입니다.",
          "count": 15
        },
        {
          "role": "user",
          "content": "안녕하세요, 이름이 무엇입니까?",
          "count": 10
        },
        {
          "role": "assistant",
          "content": "저는 HyperCLOVA X 입니다.",
          "count": 9
        }
      ]
    }
  }

Josn
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 토큰 계산기(챗 v3)

원문: https://api.ncloud-docs.com/docs/clovastudio-tokenizerhcxv3

Classic/VPC 환경에서 이용 가능합니다.

Chat Completions V3를 통해 HCX 모델에 입력한 문장의 토큰 수를 계산합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v3/api-tools/chat-tokenize/{modelName}
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	String	Required	모델 이름
<예시> HCX-005
요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
messages	Array	Required	토큰 수를 계산할 대화 메시지 목록: messages
tools	Array	Optional	Function Calling 사용 가능 도구 목록: tools
toolChoice	String | Object	Optional	Function Calling 도구 호출 동작 방식
auto : 모델이 도구 자동 호출 (String)
none : 모델이 도구 호출 없이 일반 답변 생성(String)
모델이 특정 도구 강제 호출(Object)

toolChoice.type	String	Optional	Function Calling 모델이 호출할 도구 유형
toolChoice.function	Object	Optional	Function Calling 모델이 호출할 도구
function(유효값)

toolChoice.function.name	String	Optional	Function Calling 모델이 호출할 도구 이름
responseFormat	Object	Optional	모델이 출력하는 답변 형식
responseFormat.type	String	Optional	답변 형식 타입
json (유효 값)

responseFormat.schema	Object	Optional	답변 형식 스키마
답변 형식 타입에 맞는 스키마
JSON Schema(object) (유효 값)
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
system | user | assistant | tool
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 사용자의 발화 또는 질문에 대한 답변
tool: Function Calling에 따른 처리 결과 입력

content	String | Array	Required	대화 메시지 내용
텍스트 입력(String)
텍스트, 이미지 URL로 구성하여 입력(Array): content

toolCalls	Array	Conditional	assistant의 호출 도구 정보
role이 tool인 경우 assistant의 toolCalls 요청과 같이 입력

toolCallId	String	Conditional	도구 아이디
role이 tool인 경우, 필수 입력
assistant의 toolCalls 요청과 연결하는 용도
content

content에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
type	Enum	Required	대화 메시지 내용의 형식
text | image_url
text : 텍스트
image_url : 이미지 URL

text	String	Conditional	대화 메시지 내용
텍스트 입력
type이 text인 경우, 필수 입력

imageUrl	Object	Conditional	이미지 목록
type이 image_url인 경우, imageUrl과 dataUri 중 필수 입력
턴당 이미지 1개 포함 가능
최적의 결과를 위해 text와 함께 요청 권장

imageUrl.url	String	Conditional	파일 확장자를 포함한 단일 이미지의 공개 URL
이미지 지원 사양
형식: BMP, PNG, JPG, JPEG, WEBP
크기: 0Byte 초과 20MB 이하
비율: 가로, 세로가 1:5 또는 5:1 이하
길이: 가로, 세로 중 긴 쪽은 2240px이하. 짧은 쪽은 4px 이상

dataUri	Object	Conditional	이미지 목록
type이 image_url인 경우, imageUrl과 dataUri 중 필수 입력
턴당 이미지 1개 포함 가능
최적의 결과를 위해 text와 함께 요청 권장

dataUri.data	String	Conditional	Base64로 인코딩된 이미지 문자열
이미지 지원 사양
형식: BMP, PNG, JPG, JPEG, WEBP
크기: 0Byte 초과 20MB 이하
비율: 가로, 세로가 1:5 또는 5:1 이하
길이: 가로, 세로 중 긴 쪽은 2240px이하. 짧은 쪽은 4px 이상
tools

tools에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
type	String	Required	도구 유형
function(유효값)

function	Object	Required	호출 function 정보
function.name	String	Required	function 이름
function.description	String	Required	function 설명
function.parameters	Object	Required	function 사용 시 전달되는 매개변수
properties, required
입력: 요청 예시 참조
형식: JSON Schema reference 참조
toolCalls

toolCalls에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
id	String	-	도구 식별자
type	String	-	도구 유형
function(유효값)

function	Object	-	호출 function 정보
function.name	String	-	function 이름
function.arguments	Object	-	function 사용 시 전달되는 매개변수
요청 예시

요청 예시는 다음과 같습니다.

이미지로 질의하는 경우

이미지로 질의하는 경우의 요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v3/api-tools/chat-tokenize/{modelName}' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
        {
            "role": "system",
            "content": "- 친절하게 답변하는 AI 어시스턴트입니다."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "imageUrl": [
                        {
                            "url": "https://www.******.com/image_a1b1c1.png"
                        }
                    ]
                },
                {
                    "type": "text",
                    "text": "이 사진에 대해서 설명해줘"
                }
            ]
        },
        {
            "role": "assistant",
            "content": "사진에는 어린 아이가 양에게 먹이를 주는 모습이 담겨 있습니다."
        }
    ]
}'

Shell Session
COPY
텍스트로 질의하는 경우

텍스트로 질의하는 경우의 요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v3/api-tools/chat-tokenize/{modelName}' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
	"messages":[
		{
			"content":"내일 서울 날씨 어때?",
			"role":"user"
		}
	],
	"tools":[
		{
			"type":"function",
			"function":{
				"description":"날씨를 알려줄 수 있는 도구",
				"name":"weather",
				"parameters":{
					"properties":{
						"location":{
							"description":"서울, 대전, 부산 등의 도시 이름",
							"type":"string"
						},
						"unit":{
							"enum":[
								"celsius",
								"fahrenheit"
							],
							"type":"string"
						},
						"date":{
							"description":"2023-08-01 같은 형태의 날짜 문자열. 날씨를 알고 싶은 날짜",
							"type":"string"
						}
					},
					"required":[
						"location"
					],
					"type":"object"
				}
			}
		},
		{
			"type":"function",
			"function":{
				"description":"여행지를 추천해 줄 수 있는 도구",
				"name":"travel",
				"parameters":{
					"properties":{
						"location":{
							"description":"The city and state, e.g. San Francisco, CA",
							"type":"string"
						},
						"date":{
							"description":"\"2023-08-01~2023-09-01\" 같은 형태의 날짜 쌍 문자열. 여행 날짜 범위",
							"type":"string"
						}
					},
					"required":[
						"location"
					],
					"type":"object"
				}
			}
		}
	],
    "toolChoice":"auto"
}'

Shell Session
COPY
Structured Outputs로 질의하는 경우

Structured Outputs로 질의하는 경우의 요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v3/api-tools/chat-tokenize/{modelName}' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
    "messages": [
        {
            "role": "system",
            "content": "- 미리 정의한 JSON Schema 형식에 맞춰 답변하는 AI 어시스턴트입니다."
        },
        {
            "role": "user",
            "content":  "오늘의 최고 기온은 32도, 최저 기온은 15도, 강수 확률은 30%입니다."
        }
    ],
    "responseFormat": {
        "type" : "json",
        "schema": {
            "type": "object",
            "properties": {
                "temp_high_c": {
                "type": "number",
                "description": "최고 기온(섭씨)"
                },
                "temp_low_c": {
                    "type": "number",
                    "description": "최저 기온(섭씨)"
                },
                "precipitation_percent": {
                    "type": "number",
                    "description": "강수 확률(%)",
                    "minimum": 0,
                    "maximum": 100
                }
            },
            "required": [
                "temp_high_c",
                "temp_low_c",
                "precipitation_percent"
            ]
        }
    }
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.messages	Array	-	토큰 수가 계산된 요청 대화 메시지 목록: messages
result.tools	Object	-	토큰 수가 계산된 요청 도구 목록: ToolCount
result.responseFormat	Object	-	Structured Outputs 토큰 계산 결과: ResponseFormatCount
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	-	대화 메시지의 역할
system | user | assistant | tool
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변
tool: Function Calling에 따른 처리 결과 입력

content	Object	-	메시지 내용 토큰 계산 결과: ChatMessageCount
ChatMessageCount

ChatMessageCount에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
type	Enum	Required	대화 메시지 내용의 형식
text | image_url
text : 텍스트
image_url : 이미지 URL

text	String	Conditional	대화 메시지 내용
텍스트 입력
type이 text인 경우 입력 필수

imageUrl	Object	Conditional	대화 메시지 내용
이미지 URL 입력
type이 image_url인 경우 'imageUrl'과 'dataUri' 둘 중 하나는 입력 필수
턴당 이미지 1개 포함 가능
최적의 결과를 위해 text와 함께 요청 권장

imageUrl.url	String	Conditional	파일 확장자를 포함한 단일 이미지의 공개 URL
이미지 지원 사양
확장자: BMP, PNG, JPG, JPEG, WEBP
크기: 20MB 미만
가로:세로 비율 1:5 또는 5:1 이하
장축(가로와 세로 중 긴 쪽) 길이: 2240px 이하

dataUri	Object	Conditional	대화 메시지 내용
이미지 URL 입력
type이 image_url인 경우 'imageUrl'과 'dataUri' 둘 중 하나는 입력 필수
턴당 이미지 1개 포함 가능
최적의 결과를 위해 text와 함께 요청 권장

dataUri.data	String	Conditional	Base64로 인코딩된 이미지 문자열
이미지 지원 사양
확장자: BMP, PNG, JPG, JPEG, WEBP
크기: 20MB 이하
가로:세로 비율 1:5 또는 5:1 이하
장축(가로와 세로 중 긴 쪽) 길이: 2240px 이하, 짧은 쪽은 4px 이상

count	Integer	Required	대화 메시지 내용 별 토큰 수 계산 결과
ToolCount

ToolCount에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
count	Integer	Required	도구 목록의 토큰 수 계산 결과
ResponseFormatCount

ResponseFormatCount에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
count	Integer	Required	Structured Outputs의 토큰 수 계산 결과
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "messages": [
            {
                "role": "system",
                "content": {
                    "type": "text",
                    "text": "- 친절하게 답변하는 AI 어시스턴트입니다.",
                    "count": 16
                }
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "imageUrl": {
                            "url": "https://www.******.com/image_a1b1c1.png"
                        },
                        "count": 1478
                    },
                    {
                        "type": "text",
                        "text": "이 사진에 대해서 설명해줘",
                        "count": 12
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "사진에는 어린 아이가 양에게 먹이를 주는 모습이 담겨 있습니다.",
                        "count": 20
                    }
                ]
            }
        ]
    }
}

COPY
Plain text
Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "내일 서울 날씨 어때?",
                        "count": 12
                    }
                ]
            }
        ],
        "tools": {
            "count": 230
        }
    }
}

Shell Session
COPY
Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "- 미리 정의한 JSON Schema 형식에 맞춰 답변하는 AI 어시스턴트입니다.",
                        "count": 18
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "오늘의 최고 기온은 32도, 최저 기온은 15도, 강수 확률은 30%입니다.",
                        "count": 27
                    }
                ]
            }
        ],
        "responseFormat": {
            "count": 86
        }
    }
}

Shell Session
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 토큰 계산기(임베딩 v2)

원문: https://api.ncloud-docs.com/docs/clovastudio-tokenizerembedding

Classic/VPC 환경에서 이용 가능합니다.

임베딩 v2에서 입력한 문장의 토큰 수를 계산합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/embedding/v2/tokenize
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
text	String	Required	토큰 수를 계산할 대화 메시지
1~10,000자(한글 기준)
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/embedding/v2/tokenize' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
    "text": "총 토큰 수를 알려 주세요."
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.numTokens	Integer	-	토큰 수 계산 결과
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "numTokens": 1000
    }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 슬라이딩 윈도우

원문: https://api.ncloud-docs.com/docs/clovastudio-sliding

Classic/VPC 환경에서 이용 가능합니다.

Chat Completions API 이용 시 최대 토큰 수를 초과하는 문장을 지워줍니다. 가장 오래된 순서로 대화 턴을 삭제하여 토큰을 확보하기 때문에 대화를 끊김 없이 생성할 수 있게 됩니다.

참고

슬라이딩 윈도우의 작동 방식 및 작업 과정에 대한 자세한 설명은 CLOVA Studio 사용 가이드의 API 활용
(opens in new tab)
을 참조해 주십시오.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/sliding/chat-messages/{modelName}
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	String	Required	모델 이름
<예시> HCX-003
요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
maxTokens	Integer	Required	최대 생성 토큰 수
0 ＜ maxTokens ≤ 4096 (기본값: 100)

messages	Array	Required	대화 메시지 목록: messages
최대 토큰 수에 맞게 조정 필요
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지의 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

content	String	Required	대화 메시지 내용
참고

일부 필드 입력 시 다음 내용을 확인해 주십시오.

messages: 입력한 토큰 수와 maxTokens에서 입력한 토큰 수의 합은 4096 토큰을 초과할 수 없습니다. messages에서 입력한 토큰 수는 토큰 계산 API를 호출하여 확인할 수 있습니다.
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/sliding/chat-messages/{modelName}' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
      "maxTokens" : 200,
      "messages" : [ {
        "role" : "user",
        "content" : "hello"
      } ]
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 바디

바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
최대 토큰 수에 맞게 조정한 결과

result.messages	Array	-	대화 메시지 목록: messages
messages

messages에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	-	대화 메시지의 역할
system | user | assistant
system: 역할을 규정하는 지시문
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

content	String	-	대화 메시지 내용
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "messages": [
            {
                "role": "user",
                "content": "hello"
            }
        ]
    }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 요약

원문: https://api.ncloud-docs.com/docs/clovastudio-summarization

Classic/VPC 환경에서 이용 가능합니다.

다양한 옵션을 적용하여 긴 문장을 요약합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/summarization/v2
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
texts	Array	Required	요약 대상 문장
1~35,000자(한글 기준, 공백 포함)

autoSentenceSplitter	Boolean	Optional	요약 대상 문장의 문단 분리 허용 여부
true (기본값) | false
true: 문단 분리 및 segCount, segMaxSize, segMinSize 적용
false: 문단 분리 안 함

segCount	Integer	Optional	요약 대상 문장의 문단 분리 수
-1 (기본값) | 1 이상
-1: 모델이 최적값으로 자동 수행

segMaxSize	Integer	Optional	문단 분리 시 한 문단의 최대 글자 수
1~3,000자(한글 기준, 공백 포함) (기본값: 1,000)

segMinSize	Integer	Optional	문단 분리 시 한 문단의 최소 글자 수
0~segMaxSize 값 (기본값: 300)

includeAiFilters	Boolean	Optional	AI 필터 적용 여부
true | false (기본값)
true: 적용
false: 적용 안 함
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/summarization/v2' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
            "texts": [
                "CLOVA Studio가 제공하는 다양한 기능은 다음과 같습니다. - 문장 생성: 몇 가지 키워드만 입력하면 해당 키워드를 기반으로 시나리오 창작, 자기소개서 작성, 이메일 생성, 마케팅 문구 창작 등 다양한 분야의 문장 생성. - 요약: 줄거리, 보고서, 이메일과 같이 긴 글에서 주요 요소를 파악하여 설정한 요약문 길이에 따라 글 요약. - 분류: 문장의 유형, 문서 색인, 감정, 의도와 같은 특징을 분류하거나 문단에서 주요 키워드 추출 가능. - 대화: 예제 입력을 통해 고유의 페르소나를 가진 AI를 생성하여 지식백과형 챗봇, 커스텀 챗봇 등 대화 인터페이스 제작 가능. - 문장 변환: 입력한 예제와 유사한 스타일의 문장으로 문장 형태 변환 가능 AI Filter: 민감하거나 안전하지 않은 결과물이 생성되는 것을 감지하여 알리는 AI Filter 기능 제공"
            ],
            "autoSentenceSplitter": true,
            "segCount": -1,
            "segMaxSize": 1000,
            "segMinSize": 300,
            "includeAiFilters": false
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.text	String	-	요약 결과
result.inputTokens	Integer	-	요약 대상 문장의 토큰 수
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "text": "- 클로바 스튜디오가 제공하는 다양한 기능에 대해 설명하고 있음",
        "inputTokens": 187
    }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 임베딩

원문: https://api.ncloud-docs.com/docs/clovastudio-embedding

Classic/VPC 환경에서 이용 가능합니다.

텍스트를 숫자로 표현하는 벡터화 작업을 수행합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/embedding/{modelName}
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
modelName	Enum	Required	임베딩 수행 모델
clir-emb-dolphin | clir-sts-dolphin
clir-emb-dolphin: 모든 도메인에 적용 가능한 높은 범용성을 가진 모델 (기본값)
clir-sts-dolphin: 문장의 의미를 정밀하게 측정하는 데 특화된 모델
요청 바디

바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
text	String	Required	임베딩 수행 텍스트(토큰)
1~500
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/embedding/{modelName}' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
          "text": "오늘 날씨 알려줘"
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.embedding	Array	-	임베딩 수행 결과
1,024개의 Float 목록으로 구성

result.inputTokens	Integer	-	임베딩 수행 텍스트의 토큰 수
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
      "code": "20000",
        "message": "OK"
      },
    "result": {
      "embedding": [ -0.3861295, -0.7903874, ... , 0.2994273, -0.7736456, -0.24933687 ]
      "inputTokens": 4
    }
  }

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 임베딩 v2

원문: https://api.ncloud-docs.com/docs/clovastudio-embeddingv2

Classic/VPC 환경에서 이용 가능합니다.

장문의 텍스트를 숫자로 표현하는 벡터화 작업을 수행합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/embedding/v2
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
text	String	Required	임베딩 수행 텍스트(토큰)
~8,192
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/embedding/v2/' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
          "text": "오늘 날씨 알려줘"
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.embedding	Array	-	임베딩 수행 결과
1,024개의 Float 목록으로 구성

result.inputTokens	Integer	-	임베딩 수행 텍스트의 토큰 수
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
      "code": "20000",
        "message": "OK"
      },
    "result": {
      "embedding": [ -0.3861295, -0.7903874, ... , 0.2994273, -0.7736456, -0.24933687 ]
      "inputTokens": 4
    }
  }

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

## 문단 나누기

원문: https://api.ncloud-docs.com/docs/clovastudio-segmentation

Classic/VPC 환경에서 이용 가능합니다.

문장 간 유사도를 파악하여 주제 단위로 글의 단락을 구분합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/api-tools/segmentation
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
text	Array	Required	문단 나누기를 할 문서
1~120,000자(한글 기준, 공백 포함)

alpha	Float	Optional	문단 나누기를 위한 Thresholds 값
클수록 나눠지는 문단 수 증가
-100 | -1.5~1.5 (기본값: 0.0)
-100: 모델이 최적값으로 자동 수행

segCnt	Integer	Optional	문단 나누기 수
-1 (기본값) | 1 이상
-1: 모델이 최적값으로 자동 수행

postProcess	Boolean	Optional	문단 나누기 후 원하는 길이로 문단을 합치거나 나누는 후처리 수행 여부
true | false (기본값)
true: 후처리 수행 및 관련 파라미터 적용
false: 후처리 수행하지 않음

postProcessMaxSize	Integer	Optional	postProcess 후처리 후 한 문단의 최대 글자 수
1 이상 (기본값: 1,000)

postProcessMinSize	Integer	Optional	postProcess 후처리 후 한 문단의 최소 글자 수
-1 | 0~postProcessMaxSize 값 (기본값: 300)
-1: 최소 단위로 자동 설정
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/api-tools/segmentation' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
          "text": "노트는 어떻게 생성할 수 있나요?\n두 가지 방법이 있습니다.\n클로바노트 앱에서 추가 버튼을 눌러 녹음을 시작하거나, 스마트폰에 저장해둔 녹음 파일을 불러오면 노트가 생성된답니다.\n이렇게 만들어진 노트는 앱뿐만 아니라 PC의 클로바노트 웹사이트에서도 연동되어 확인하실 수 있는데요.\n클로바노트 사이트에서는 저장된 녹음파일을 불러오면 노트를 만들 수 있답니다.\n북마크는 어떻게 사용하는 건가요?\n클로바노트 앱 화면에서 녹음 중간에 북마크 버튼을 누르면, 아래처럼 표시되어 녹음을 마치고 나서도 필요한 구간을 쉽게 찾을 수 있죠.\n평소 녹음을 마치고 나면 분명히 다시 찾아보고 싶은 녹음 구간이 있었을 거예요.\n그런 순간을 위해 북마크를 제공하고 있답니다.\n그럼 녹음한 음성은 어떻게 들어볼 수 있나요?\n생성된 노트에서 기록된 대화를 선택하면 녹음 음성을 다시 들어볼 수 있답니다.\n만약 음성 기록이 잘못된 구간이 있다면 다시 한 번 음성을 들어보고 편집 버튼을 눌러 쉽게 바로잡을 수 있죠.",
          "alpha": -100,
          "segCnt": -1,
          "postProcess": false,
          "postProcessMaxSize": 2000,
          "postProcessMinSize": 500
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태 참조
result	Object	-	응답 결과
result.topicSeg	Array	-	문단 나누기 결과
result.span	Array	-	문단이 나눠진 텍스트의 인덱스
문단이 나눠진 위치 확인
[] (기본값)

result.inputTokens	Integer	-	문단 나누기 대상 문서의 토큰
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
    "status": {
        "code": "20000",
        "message": "OK"
    },
    "result": {
        "topicSeg": [
            [
                "노트는 어떻게 생성할 수 있나요?",
                "두 가지 방법이 있습니다."
            ],
            [
                "클로바노트 앱에서 추가 버튼을 눌러 녹음을 시작하거나, 스마트폰에 저장해둔 녹음 파일을 불러오면 노트가 생성된답니다.",
                "이렇게 만들어진 노트는 앱뿐만 아니라 PC의 클로바노트 웹사이트에서도 연동되어 확인하실 수 있는데요.",
                "클로바노트 사이트에서는 저장된 녹음파일을 불러오면 노트를 만들 수 있답니다."
            ],
            [
                "북마크는 어떻게 사용하는 건가요?",
                "클로바노트 앱 화면에서 녹음 중간에 북마크 버튼을 누르면, 아래처럼 표시되어 녹음을 마치고 나서도 필요한 구간을 쉽게 찾을 수 있죠.",
                "평소 녹음을 마치고 나면 분명히 다시 찾아보고 싶은 녹음 구간이 있었을 거예요.",
                "그런 순간을 위해 북마크를 제공하고 있답니다."
            ],
            [
                "그럼 녹음한 음성은 어떻게 들어볼 수 있나요?",
                "생성된 노트에서 기록된 대화를 선택하면 녹음 음성을 다시 들어볼 수 있답니다.",
                "만약 음성 기록이 잘못된 구간이 있다면 다시 한 번 음성을 들어보고 편집 버튼을 눌러 쉽게 바로잡을 수 있죠."
            ]
        ],
        "span": [
            [
                0,
                1
            ],
            [
                2,
                3,
                4
            ],
            [
                5,
                6,
                7,
                8
            ],
            [
                9,
                10,
                11
            ]
        ],
        "inputTokens": 330
    }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
서버 공통 오류 문제(5xx)

---

# 라우터

## 라우터

원문: https://api.ncloud-docs.com/docs/clovastudio-router

Classic/VPC 환경에서 이용 가능합니다.

특정 라우터의 API를 호출하여 입력된 요청을 적절한 도메인으로 분류하고, 설정된 필터 조건에 해당하는지 판별합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/routers/{router-id}/versions/{version}/route
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
router-id	String	Required	라우터 아이디
version	Integer	Required	라우터 버전
1 ≤ version
요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
query	String	Required	입력
chatHistory	Array	Optional	대화 메시지 이력: chatHistory
chatHistory

chatHistory에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
user: 사용자의 발화/질문

content	String	Required	대화 메시지 내용
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/routers/{router-id}/versions/{version}/route' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{
  "query" : "미세먼지 정보 알려줘",
  "chatHistory" : [ {
    "role" : "user",
    "content" : "내일 서울의 강수 예보 알려줘"
  } ]
}'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태
result	Object	-	응답 결과
result.domain	Object	-	도메인 결과
result.domain.result	String	-	도메인 판별 결과
일치하는 도메인이 없는 경우 빈 문자열 표시

result.domain.called	Boolean	-	도메인 판별 수행 여부
true | false
true: 수행함
false: 수행 안 함

result.blockedContent	Object	-	콘텐츠 필터 결과
result.blockedContent.result	Array	-	콘텐츠 필터 판별 결과
일치하는 필터 없는 경우 빈 목록 표시

result.blockedContent.called	Boolean	-	콘텐츠 필터 판별 수행 여부
true | false
true: 수행함
false: 수행 안 함

result.safety	Object	-	세이프티 필터 결과
result.safety.result	Array	-	세이프티 필터 판별 결과
일치하는 필터 없는 경우 빈 목록 표시

result.safety.called	Boolean	-	세이프티 필터 판별 수행 여부
true | false
true: 수행함
false: 수행 안 함

result.usage	Object	-	토큰 수 정보
result.usage.promptTokens	Integer	-	입력 토큰 수
result.usage.completionTokens	Integer	-	생성 토큰 수
result.usage.totalTokens	Integer	-	전체 토큰 수
promptTokens + completionTokens
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
  "status": {
    "code": "20000",
    "message": "OK"
  },
  "result": {
    "domain": {
      "result": "지역 검색",
      "called": true
    },
    "blockedContent": {
      "result": ["UnsupportedRegion"],
      "called": true
    },
    "safety": {
      "result": [],
      "called": true
    },
    "usage": {
      "promptTokens": 425,
      "completionTokens": 62,
      "totalTokens": 487
    }
  }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
클라이언트 스킬 오류 문제(4xx)
서버 공통 오류 문제(5xx)
서버 스킬 오류 문제(5xx)

---

# 스킬 트레이너

## 스킬셋

원문: https://api.ncloud-docs.com/docs/clovastudio-generateskillsetfinalanswer

Classic/VPC 환경에서 이용 가능합니다.

특정 스킬셋의 API를 호출하여 적절한 답변을 생성합니다.

요청

요청 형식을 설명합니다. 요청 형식은 다음과 같습니다.

메서드	URI
POST	/v1/skillsets/{skillset-id}/versions/{version}/final-answer
요청 헤더

CLOVA Studio API에서 공통으로 사용하는 헤더에 대한 정보는 CLOVA Studio 요청 헤더를 참조해 주십시오.

요청 경로 파라미터

요청 경로 파라미터에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
skillset-id	String	Required	스킬셋 아이디
version	Integer	Required	스킬셋 버전
1 ≤ version
요청 바디

요청 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
query	String	Required	질의 내용
tokenStream	Boolean	Optional	답변 생성 시 토큰 스트리밍 사용 여부
false | true
false: 사용 안 함
true: 사용

chatHistory	Array	Optional	답변 생성 이력: chatHistory
requestOverride	Object	Optional	모든 API에 적용할 호출 옵션
requestOverride.baseOperation	Object	Optional	모든 API에 적용할 호출 옵션 정보
requestOverride.baseOperation.header	Object	Optional	모든 API에 적용할 요청 헤더
requestOverride.baseOperation.query	Object	Optional	모든 API에 적용할 요청 쿼리 파라미터
requestOverride.baseOperation.requestBody	Object	Optional	모든 API에 적용할 요청 바디
GET 메서드 API인 경우 미적용

requestOverride.operations	Array	Optional	특정 API에 적용할 호출 옵션: operations
chatHistory

chatHistory에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
role	Enum	Required	대화 메시지 역할
user | assistant
user: 사용자의 발화 또는 질문
assistant: 모델의 답변

content	String	Required	대화 메시지 내용
operations

operations에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
operationId	String	Conditional	특정 API의 오퍼레이션 아이디
operations를 입력할 경우 필수 입

header	Object	Optional	특정 API에 적용할 요청 헤더
query	Object	Optional	특정 API에 적용할 요청 쿼리 파라미터
requestBody	Object	Optional	특정 API에 적용할 요청 바디
GET 메서드 API인 경우 미적용
요청 예시

요청 예시는 다음과 같습니다.

Code snippet
curl --location --request POST 'https://clovastudio.stream.ntruss.com/v1/skillsets/{skillset-id}/versions/{version}/final-answer' \
--header 'Authorization: Bearer {API Key}' \
--header 'X-NCP-CLOVASTUDIO-REQUEST-ID: {Request ID}' \
--header 'Content-Type: application/json' \
--data '{  
    "query": "내일 날씨는 어때?",
    "tokenStream": true,
    "chatHistory": [
        {
            "role": "user",
            "content": "오늘 서울 날씨 어때?"
         },
        {
            "role": "assistant",
            "content": "폭풍전야입니다."
         }
     ],
     "requestOverride": {
        "baseOperation": {
            "query": {
                "appid": "appid-11223344"
                }
            }
        }
    }'

Shell Session
COPY
응답

응답 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

헤더	필수 여부	설명
Content-Type	-	응답 데이터의 형식
application/json
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
status	Object	-	응답 상태
result	Object	-	응답 결과
result.finalAnswer	String	-	모델의 최종 실행 결과
마지막까지 실행되지 않으면 빈 문자열 반환

result.tokenCount	Integer	-	답변 생성 시 측정된 토큰 수
result.useTask	Boolean	-	호출한 모델의 학습 여부
false | true
false: 학습하지 않음
true: 학습 완료

result.apiResult	Array	-	호출한 API 결과: apiResult
apiResult

apiResult에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
url	String	-	답변 과정에서 호출한 API URL
requestBody	String	-	답변 과정에서 호출한 API 요청 바디
responseBody	String	-	답변 과정에서 호출한 API 응답 바디
apiOrder	Integer	-	API 호출 결과에 상관없이 응답 순서를 고정하기 위한 정렬 기준
operationId	String	-	답변 과정에서 호출한 API Spec의 오퍼레이션 아이디
nameForHuman	String	-	답변 과정에서 호출한 API가 등록된 스킬의 이름
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
{
  "status": {
    "code": "20000",
    "message": "OK"
  },
  "result": {
    "finalAnswer": "내일 서울 날씨는 맑음이며, 온도는 약 27도 정도로 예상됩니다.",
    "tokenCount": 1032,
    "apiResult": [
      {
        "url": "http://example.com?numOfRows=1&location=서울&date=20240530",
        "requestBody": "string",
        "responseBody": "string",
        "apiOrder": 1,
        "operationId": "weatherAPI",
        "nameForHuman": "WeatherSkill"
      }
    ]
  }
}

JSON
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
클라이언트 스킬 오류 문제(4xx)
서버 공통 오류 문제(5xx)
서버 스킬 오류 문제(5xx)
응답 스트림

생성되는 토큰을 하나씩 출력하도록 토큰 스트리밍을 사용할 수 있습니다. 토큰 스트리밍 형식을 설명합니다.

응답 헤더

응답 헤더에 대한 설명은 다음과 같습니다.

필드	필수 여부	설명
Accept	-	응답 데이터의 형식
text/event-stream
응답 바디

응답 바디에 대한 설명은 다음과 같습니다.

필드	타입	필수여부	설명
selectedSkill	Object	-	선택된 스킬 이름
Planning event에서만 표시

finalAnswer	String	-	모델의 최종 실행 결과
마지막까지 실행되지 않으면 빈 문자열 반환
FinalAnswer event에서만 표시

tokenCount	Integer	-	이벤트에서 사용된 토큰 수
apiResult	Object	-	답변 과정에서 호출한 API 결과
FinalAnswer event에서만 표시

apiResult.url	String	-	답변 과정에서 호출한 API URL
apiResult.requestBody	String	-	답변 과정에서 호출한 API 요청 바디
apiResult.responseBody	String	-	답변 과정에서 호출한 API 응답 바디
apiResult.apiOrder	Integer	-	API 호출 결과에 상관없이 응답 순서를 고정하기 위한 정렬 기준
apiResult.operationId	String	-	답변 과정에서 호출한 API Spec의 오퍼레이션 아이디
apiResult.nameForHuman	String	-	답변 과정에서 호출한 API가 등록된 스킬의 이름
Token Event

TokenEvent에 대한 설명은 다음과 같습니다.

필드	타입	필수 여부	설명
probs	Array	-	응답 후보 토큰의 목록 및 각 토큰의 확률값
stopReason	String	-	결괏값 생성 중단의 이유(일반적으로 마지막 이벤트에 전달)
length | end_token | stop_before
length: 길이 제한
end_token: 토큰 수 제한
stop_before: 답변 생성 중 stopBefore 설정값 출현

text	String	-	완전한 텍스트 페어
응답 예시

응답 예시는 다음과 같습니다.

성공

호출이 성공한 경우의 응답 예시는 다음과 같습니다.

Code snippet
id: aabdfe-dfgwr-edf-hpqwd-f2asd-g
event: planning
data: {"selectedSkill": {["nameForHuman":"호텔 검색"]}, "tokenCount": 432}
id: aabdfe-dfgwr-edf-hpqwd-f1asd-g
event: cot
data: {"apiResult": [{"url": "https://example.com/search_reviews_get?keyword=지하철역 접근성 좋은", "requestBody": "keyword=지하철역 접근성 좋은", "responseBody": "[{\"review_id\": 5,
\"review_date\": \"20230809\", \"reviewer\": \"ClaudeCalder\", \"rating\": 4.0, \"content\": \"사우나,
수영장 등 부대시설이 없어서 아쉬웠지만 가격이 저렴해서 좋았어요. 근처에 지하철역도 있고 편의점도 있어서 접근성이
좋아요. 잠시 머물기엔 딱 입니다.\", \"hotel_name\": \"Movenpick Hotel\", \"address\": \"서울 광진구
워커힐로 120\", \"room_name\": \"City View\", \"good_cnt\": 9, \"bad_cnt\": 0, \"rating_service\":
3.0, \"rating_clean\": 4.0, \"rating_room\": 4.0}]", "apiOrder": 1}], "tokenCount": 2401 }
id: aabdfe-dfgwr-edf-hpqwd-f2asd-g
event: finalAnswer
data: {"finalAnswer": "서울에서 지하철역 접근성 좋은 호텔은 Movenpick Hotel이며, 서울 광진구 워커힐로 120에
위치해 있습니다.", "apiResult": [{"url": "https://example.com/search_reviews_get?keyword=지하철역 접근성 좋은", "requestBody": "keyword=지하철역 접근성 좋은", "responseBody":
"[{\"review_id\": 5, \"review_date\": \"20230809\", \"reviewer\": \"ClaudeCalder\", \"rating\": 4.0,
\"content\": \"사우나, 수영장 등 부대시설이 없어서 아쉬웠지만 가격이 저렴해서 좋았어요. 근처에 지하철역도 있고
편의점도 있어서 접근성이 좋아요. 잠시 머물기엔 딱입니다.\", \"hotel_name\": \"Movenpick Hotel\",
\"address\": \"서울 광진구 워커힐로 120\", \"room_name\": \"City View\", \"good_cnt\": 9, \"bad_cnt\":
0, \"rating_service\": 3.0, \"rating_clean\": 4.0, \"rating_room\": 4.0}]", "apiOrder": 1}],
"tokenCount": 214 }
...

Shell Session
COPY
실패

호출이 실패한 경우의 응답 예시는 다음과 같습니다.

클라이언트 공통 오류 문제(4xx)
클라이언트 스킬 오류 문제(4xx)
서버 공통 오류 문제(5xx)
서버 스킬 오류 문제(5xx)

---

# CLOVA Studio 문제 해결

## CLOVA Studio 문제 해결

원문: https://api.ncloud-docs.com/docs/clovastudio-troubleshoot

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio 서비스를 이용하면서 겪을 수 있는 문제 상황과 해결 방법을 안내합니다. 각 문제 상황을 클릭하면 관련 페이지로 이동합니다.

요청 처리 성공(2xx)

사용자가 겪을 수 있는 일반적인 문제 상황은 다음과 같습니다.

20000 OK
API 호출이 성공했고, 응답 상태 코드는 20000이라고 표시됩니다.

20400 No content
API 호출이 성공했고, 응답 상태 코드는 20400이라고 표시됩니다.

참고

성공 관련 HTTP 상태 코드는 문제 상황과 무관하지만, API 호출 결과의 정상 여부를 판단하여 문제를 인지하는 기준이 되므로 문제 해결 가이드에서 안내합니다.

클라이언트 공통 오류 문제(4xx)

사용자가 겪을 수 있는 클라이언트 공통 오류 관련 문제 상황은 다음과 같습니다.

40000 Bad request
API 호출이 실패했고, 응답 상태 코드는 40000이라고 표시됩니다.

40001 Invalid parameter
API 호출이 실패했고, 응답 상태 코드는 40001이라고 표시됩니다.

40002 Unsupported parameter
API 호출이 실패했고, 응답 상태 코드는 40002이라고 표시됩니다.

40003 Context length exceeded, Image limit exceeded
API 호출이 실패했고, 응답 상태 코드는 40003이라고 표시됩니다.

40004 Text empty
API 호출이 실패했고, 응답 상태 코드는 40004라고 표시됩니다.

40005 Unavailable output
API 호출이 실패했고, 응답 상태 코드는 40005라고 표시됩니다.

40009 Unsupported input format, Unsupported function, Unsupported input format
API 호출이 실패했고, 응답 상태 코드는 40009라고 표시됩니다.

40055 Structured Outputs Error
API 호출이 실패했고, 응답 상태 코드는 40055라고 표시됩니다.

40060 Unsupported image format
API 호출이 실패했고, 응답 상태 코드는 40060이라고 표시됩니다.

40061 File size error
API 호출이 실패했고, 응답 상태 코드는 40061이라고 표시됩니다.

40063 Invalid image size, Invalid image ratio, Invalid image file, Invalid image url, Image download failed, Image processing error
API 호출이 실패했고, 응답 상태 코드는 40063이라고 표시됩니다.

40080 Model not found
API 호출이 실패했고, 응답 상태 코드는 40080이라고 표시됩니다.

40082 Model fade out
API 호출이 실패했고, 응답 상태 코드는 40082라고 표시됩니다.

40083 Model no resource
API 호출이 실패했고, 응답 상태 코드는 40083이라고 표시됩니다.

40084 Unsupported API for model
API 호출이 실패했고, 응답 상태 코드는 40082라고 표시됩니다.

40100 Unauthorized
API 호출이 실패했고, 응답 상태 코드는 40100이라고 표시됩니다.

40101 Invalid signature
API 호출이 실패했고, 응답 상태 코드는 40101이라고 표시됩니다.

40102 Invalid access token
API 호출이 실패했고, 응답 상태 코드는 40102라고 표시됩니다.

40103 Access token expired
API 호출이 실패했고, 응답 상태 코드는 40103이라고 표시됩니다.

40104 Invalid key
API 호출이 실패했고, 응답 상태 코드는 40104라고 표시됩니다.

40170 No subscription request history found. Please request a subscription to use
API 호출이 실패했고, 응답 상태 코드는 40170이라고 표시됩니다.

40300 Forbidden
API 호출이 실패했고, 응답 상태 코드는 40300이라고 표시됩니다.

40301 No ownership
API 호출이 실패했고, 응답 상태 코드는 40301이라고 표시됩니다.

40400 Not found, File not found
API 호출이 실패했고, 응답 상태 코드는 40400이라고 표시됩니다.

40600 Not Acceptable
API 호출이 실패했고, 응답 상태 코드는 40600이라고 표시됩니다.

40800 Request timeout
API 호출이 실패했고, 응답 상태 코드는 40800이라고 표시됩니다.

41300 Request body size exceeded
API 호출이 실패했고, 응답 상태 코드는 41300이라고 표시됩니다.

41500 MediaType error
API 호출이 실패했고, 응답 상태 코드는 41500이라고 표시됩니다.

41501 No multipart boundary Content-Type
API 호출이 실패했고, 응답 상태 코드는 41501이라고 표시됩니다.

42400 Processing Failed
API 호출이 실패했고, 응답 상태 코드는 42400이라고 표시됩니다.

42900 Too many requests
API 호출이 실패했고, 응답 상태 코드는 42900이라고 표시됩니다.

42901 Too many requests - rate exceeded
API 호출이 실패했고, 응답 상태 코드는 42901이라고 표시됩니다.

42902 Too many requests - overloaded
API 호출이 실패했고, 응답 상태 코드는 42902이라고 표시됩니다.

42903 Too many requests - image queue
API 호출이 실패했고, 응답 상태 코드는 42903이라고 표시됩니다.

클라이언트 스킬 오류 문제(4xx)

사용자가 겪을 수 있는 클라이언트 스킬 오류 관련 문제 상황은 다음과 같습니다.

61002 Missing input value
API 호출이 실패했고, 응답 상태 코드는 61002이라고 표시됩니다.

61004 Invalid action input
API 호출이 실패했고, 응답 상태 코드는 61004이라고 표시됩니다.

61005 Missing model url
API 호출이 실패했고, 응답 상태 코드는 61005이라고 표시됩니다.

62001 Invalid input value
API 호출이 실패했고, 응답 상태 코드는 62001이라고 표시됩니다.

63001 Invalid action in cot
API 호출이 실패했고, 응답 상태 코드는 63001이라고 표시됩니다.

63002 Requests_* action not in cot
API 호출이 실패했고, 응답 상태 코드는 63002이라고 표시됩니다.

64400 {HyperCLOVA error message}
API 호출이 실패했고, 응답 상태 코드는 64400이라고 표시됩니다.

65001 {HyperCLOVA error message}
API 호출이 실패했고, 응답 상태 코드는 65001이라고 표시됩니다.

65400 {HyperCLOVA error message}
API 호출이 실패했고, 응답 상태 코드는 65400이라고 표시됩니다.

64429 {HyperCLOVA error message}
API 호출이 실패했고, 응답 상태 코드는 64429이라고 표시됩니다.

서버 공통 오류 문제(5xx)

사용자가 겪을 수 있는 서버 공통 오류 관련 문제 상황은 다음과 같습니다.

50000 Internal server error
API 호출이 실패했고, 응답 상태 코드는 50000이라고 표시됩니다.

50100 Not yet implemented
API 호출이 실패했고, 응답 상태 코드는 50100이라고 표시됩니다.

50400 Gateway timeout
API 호출이 실패했고, 응답 상태 코드는 50400이라고 표시됩니다.

서버 스킬 오류 문제(5xx)

사용자가 겪을 수 있는 서버 스킬 오류 관련 문제 상황은 다음과 같습니다.

64000 HyperCLOVA API error url: {url}
API 호출이 실패했고, 응답 상태 코드는 64000이라고 표시됩니다.

64424 {HyperCLOVA error message}
API 호출이 실패했고, 응답 상태 코드는 64424라고 표시됩니다.

64500 {HyperCLOVA error message}
API 호출이 실패했고, 응답 상태 코드는 64500이라고 표시됩니다.

65002 {HyperCLOVA error message}
API 호출이 실패했고, 응답 상태 코드는 65002라고 표시됩니다.

참고

6xx로 시작하지만 서버 스킬 오류 관련 상태 코드인 경우, 서버 스킬 오류 문제(5xx)에서 함께 안내합니다.

둘러볼 콘텐츠 

네이버 클라우드 플랫폼에서는 고객에게 도움을 주기 위해 다양한 방식으로 정보를 제공하고 있습니다. CLOVA Studio 서비스 이용 시 활용할 수 있는 유용한 콘텐츠를 안내합니다.

네이버 클라우드 플랫폼 온라인 교육: 네이버클라우드플랫폼 API 활용하기
네이버 비즈니스 스쿨 온라인 교육: CLOVA Studio
참고

이 가이드에서 필요한 정보를 찾지 못했거나 추가로 필요한 정보가 있으신 경우, 언제든지 아래의 피드백 아이콘을 클릭하여 의견을 보내 주십시오. 전달해 주신 의견을 참고하여 더 유용한 정보를 제공하겠습니다.

---

## 요청 처리 성공(2xx)

원문: https://api.ncloud-docs.com/docs/clovastudio-troubleshoot-2xx

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio 서비스를 이용하면서 다음과 같은 문제를 겪을 수 있습니다. 문제별 원인과 해결 방법을 확인하고 적절하게 조치해 주십시오.

HTTP 상태 코드	코드	메시지	원인	해결 방법
200	20000	OK	요청 처리 성공	-
204	20400	No content	요청 처리 성공, 콘텐츠를 반환하지 않음	-
참고
성공 관련 HTTP 상태 코드는 문제 상황과 무관하지만, API 호출 결과의 정상 여부를 판단하여 문제를 인지하는 기준이 되므로 문제 해결 가이드에서 안내합니다.
HTTP 상태 코드를 참고하도록 시스템을 구성하면 안정적인 운영에 도움이 됩니다.

---

## 클라이언트 공통 오류 문제(4xx)

원문: https://api.ncloud-docs.com/docs/clovastudio-troubleshoot-c4xx

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio 서비스를 이용하면서 다음과 같은 문제를 겪을 수 있습니다. 문제별 원인과 해결 방법을 확인하고 적절하게 조치해 주십시오.

HTTP 상태 코드	코드	메시지	원인	해결 방법
400	40000	Bad request	잘못된 요청	API 명세를 확인하여 요청 구문 점검
400	40000	Each user message can contain only one image	턴당 이미지 2개 이상 포함	턴당 이미지 1개 포함으로 수정
400	40001	Invalid parameter	잘못된 요청 파라미터	파라미터의 지원 범위에 맞게 값을 조정하거나 API 요청 형식의 오류 수정 (메시지 내 복수 파라미터가 언급된 경우, 동시 이용 불가 기능 중 이용하고자 하는 기능 명시 필요)
400	40002	Unsupported parameter	지원하지 않는 요청 파라미터	오픈AI 호환성을 지원하지 않는 파라미터를 제외하는 등의 조정을 통해 수정
400	40003	Context length exceeded	너무 긴 요청	모델이 처리 가능한 토큰 수를 초과하지 않도록 입력된 텍스트의 길이 또는 포함한 이미지 수를 조정하거나, 파라미터에서 Maximum tokens를 낮춘 후 요청
400	40003	Image limit exceeded	요청당 이미지 최대 포함 수 초과	요청당 이미지 5개 이하로 수정
400	40004	Text empty	빈 텍스트로 요청	요청 바디에서 비어 있는 내용을 채운 후 요청
400	40005	Unavailable output	결과를 제공할 수 없는 요청	-
400	40009	Unsupported function	지원하지 않는 기능 요청	요청 구문의 tuningType 지원 여부 또는 Chat Completions /Completions 지원 여부 확인
400	40009	Unsupported function	지원하지 않는 도구(tool) 요청	요청 처리가 가능한 도구를 선택 또는 요청에서 해당 도구 지원 여부 확인
400	40009	Unsupported input format	모델이 요청한 인풋 타입을 처리할 수 없는 경우	요청한 인풋 타입을 처리할 수 있는 모델로 변경하거나, 요청을 수정
400	40055	Invalid response format schema	지원하지 않는 형식의 응답 스키마	지원하는 형식의 응답 스키마로 변경
400	40060	Unsupported image format	지원하지 않는 형식의 이미지 포함	BMP, PNG, JPG, JPEG, WEBP 형식의 이미지로 변경
400	40061	File size error	지원하지 않는 이미지 크기	0Byte 초과 20MB 이하 크기의 이미지로 변경
400	40063	Invalid image size	이미지 길이 초과	가로, 세로 중 긴 쪽은 2240px 이하, 짧은 쪽은 4px 이상의 이미지로 요청
400	40063	Invalid image ratio	지원하지 않는 이미지 비율	가로, 세로 비율이 1:5 또는 5:1 이하의 이미지로 변경
400	40063	Invalid image file	처리할 수 없는 이미지	정상적인 이미지 파일인지 확인 후 다시 시도
400	40063	Invalid image url	이미지를 찾을 수 없는 URL	정상적으로 이미지를 가져올 수 있는 URL 인지 확인 후 다시 시도
400	40063	Image download failed	모델이 이미지 다운로드 실패	잠시 후 다시 시도
400	40063	Image processing error	모델이 이미지 처리 실패	잠시 후 다시 시도
400	40080	Model not found	모델 찾을 수 없음	모델 이름 확인 후 요청
400	40082	Model fade out	모델 지원 종료	지원하는 모델로 변경하여 요청
400	40083	Model no resource	모델에 할당된 자원 없음	이용 신청 해지 및 계약 종료 여부 확인
400	40084	Unsupported API for model	미지원 모델로 요청	지원 모델로 요청하거나 해당 모델을 지원하는 API로 요청
401	40100	Unauthorized	인증 실패	CLOVA Studio 서비스의 인증 방식에 알맞은 인증 정보 확인 또는 서비스 앱 등록 여부 확인
401	40101	Invalid signature	유효하지 않은 요청 서명	유효한 NCP IAM Key, Secret으로 서명 재생성
401	40102	Invalid Authentication Type	유효하지 않은 인증 방식	CLOVA Studio에서 유효한 인증 방식으로 재요청
401	40104	Invalid key	유효하지 않은 인증 키	유효한 API 키 확인 후 재요청
401	40170	No subscription request history found. Please request a subscription to use	CLOVA Studio 이용 신청 이력을 찾을 수 없음	네이버 클라우드 플랫폼 콘솔에서 CLOVA Studio 서비스의 이용 신청 여부 확인
403	40300	Forbidden	서버 작업 거부	요청 기능에 대한 사용 권한 소유 여부 확인
403	40301	No ownership	소유권 없음	요청 기능에 대한 사용 권한 소유 여부 확인
404	40400	Not found	요청 리소스 찾지 못함	요청 구문이 유효한지 확인
404	40400	File not found	Object Storage 버킷에서 요청 리소스 찾지 못함	요청 구문(파일 경로)이 유효한지 확인
406	40600	Not Acceptable	잘못된 미디어 형식	미디어 형식 유효한지 확인
408	40800	Request timeout	요청 처리 시간 초과	요청 다시 시도
408	40800	Image I/O timeout	모델의 이미지 다운로드 처리 시간 초과	최대 이용량을 초과하지 않도록 요청을 제어하거나 다시 시도
413	41300	Request body size exceeded	요청 바디 크기 초과	50MB 이하로 수정 후 요청
415	41500	MediaType error	지원하지 않는 미디어 형식	미디어 형식 유효한지 확인
415	41501	No multipart boundary Content-Type	multipart 사용이 필요하지만 형식에 맞지 않는 요청	multipart 사용 시 필요한 형식으로 변경하여 요청
424	42400	Processing Failed	요청 처리 중 일부 항목에 문제 발생	요청 형식의 정합성 확인 후 다시 시도
429	42900	Too many requests	너무 많은 요청	사전 고지된 이용량 제어 정책에 따라 설정된 최대 이용량을 초과하지 않도록 요청 시 응답 헤더의 관련 정보를 확인하여 최대 이용량 범위 이내로 제어하거나 Exponential backoff 등의 방식으로 재시도 처리
429	42901	Too many requests - rate exceeded	너무 많은 요청 (최대 이용량 초과)	사전 고지된 이용량 제어 정책에 따라 설정된 최대 이용량을 초과하지 않도록 요청 시 응답 헤더의 관련 정보를 확인하여 최대 이용량 범위 이내로 제어하거나 Exponential backoff 등의 방식으로 재시도 처리
429	42902	Too many requests - overloaded	너무 많은 요청 (트래픽 과다)	: 한정된 GPU 인프라 기반의 컴퓨팅 리소스로 인해 사용자가 설정된 최대 이용량 이내로 서비스를 이용하더라도 인프라 상황 및 트래픽에 따라 처리 지연이 발생하거나 실패할 수 있음
429	42903	Too many requests - image queue	너무 많은 이미지 요청 (처리 지연)	잠시 후 다시 시도
참고

HTTP 상태 코드를 참고하도록 시스템을 구성하면 안정적인 운영에 도움이 됩니다.

---

## 클라이언트 스킬 오류 문제(4xx)

원문: https://api.ncloud-docs.com/docs/clovastudio-troubleshoot-s4xx

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio 서비스를 이용하면서 다음과 같은 문제를 겪을 수 있습니다. 문제별 원인과 해결 방법을 확인하고 적절하게 조치해 주십시오.

HTTP 상태 코드	코드	메시지	원인	해결 방법
400	61002	Missing input value	입력 값 누락	유저쿼리 누락이나 오류가 없는 지 점검
400	61004	Invalid action input	API 호출 실패	
올바른 액션 입력 값을 생성하도록 데이터를 수정 및 학습한 뒤 재호출
API 응답 시간이 30초를 초과하지 않는지 점검

400	61005	Missing model url	모델 경로 누락	문의 채널에 문의
400	62001	Invalid input value	쿼리 분석 실패	스킬셋에 적합한 유저쿼리로 다시 시도하거나 Description for model 값 수정
400	63001	Invalid action in cot	스킬 호출 실패	스킬셋과 연관된 유저쿼리로 다시 시도
400	63002	Requests_* action not in cot	API 호출 누락	스킬셋과 연관된 유저쿼리로 다시 시도
400	64400	{HyperCLOVA error message}	토큰 수 초과	최대 처리 가능한 토큰 수를 초과하지 않도록 입력된 텍스트의 길이를 줄이거나, API Spec 확장 기능을 통해 API 응답을 줄인 후 요청
400	65001	Invalid labels detected	라우터 모델 생성 오류	도메인 및 필터 이름을 변경하거나 다른 쿼리로 다시 시도
400	65400	{HyperCLOVA error message}	라우터 토큰 수 초과	최대 토큰 수를 초과하지 않도록 입력 텍스트(사용자 입력, 도메인 설명, 필터 설명 등)의 길이를 줄인 후 요청
429	64429	{HyperCLOVA error message}	요청 수 초과	최대 이용량을 초과하지 않도록 요청을 제어하거나 다시 시도
참고

HTTP 상태 코드를 참고하도록 시스템을 구성하면 안정적인 운영에 도움이 됩니다.

---

## 서버 공통 오류 문제(5xx)

원문: https://api.ncloud-docs.com/docs/clovastudio-troubleshoot-c5xx

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio 서비스를 이용하면서 다음과 같은 문제를 겪을 수 있습니다. 문제별 원인과 해결 방법을 확인하고 적절하게 조치해 주십시오.

HTTP 상태 코드	코드	메시지	원인	해결 방법
500	50000	Internal server error	내부 서버 오류	서버 상태 점검 후 다시 요청
501	50100	Not yet implemented	구현되지 않은 API 호출	API 지원 여부 확인
504	50400	Gateway timeout	게이트웨이 처리 시간 초과	서버 상태 점검 후 다시 요청
참고

HTTP 상태 코드를 참고하도록 시스템을 구성하면 안정적인 운영에 도움이 됩니다.

---

## 서버 스킬 오류 문제(5xx)

원문: https://api.ncloud-docs.com/docs/clovastudio-troubleshoot-s5xx

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio 서비스를 이용하면서 다음과 같은 문제를 겪을 수 있습니다. 문제별 원인과 해결 방법을 확인하고 적절하게 조치해 주십시오.

HTTP 상태 코드	코드	메시지	원인	해결 방법
500	64000	Model unavailable	응답 없음	서버 상태 점검 후 다시 요청
500	64424	Model generation failed	HyperCLOVA 생성 실패	서버 상태 점검 후 다시 요청
500	64500	Model server error	모델 서버 오류	서버 상태 점검 후 다시 요청
500	65002	Response parsing failed	라우터 모델 응답 파싱 실패	서버 상태 점검 후 다시 요청
참고

HTTP 상태 코드를 참고하도록 시스템을 구성하면 안정적인 운영에 도움이 됩니다.

---

# CLOVA Studio Exclusive 지표

## CLOVA Studio Exclusive 지표

원문: https://api.ncloud-docs.com/docs/clovastudio-exclusivevpc-metric

VPC 환경에서 이용 가능합니다.

CLOVA Studio Exclusive 서비스의 성능/운영 지표(메트릭) 관련 정보를 안내합니다. 성능/운영 지표는 네이버 클라우드 플랫폼의 Cloud Insight 서비스를 통해 통합 관리할 수 있으며, 다양한 모니터링에 활용할 수 있습니다.

참고

성능/운영 지표를 모니터링에 활용하는 방법은 Cloud Insight API 개요를 참조해 주십시오.

기본 정보

성능/운영 지표를 활용하기 위한 CLOVA Studio Exclusive 서비스의 기본 정보는 다음과 같습니다.

상품 이름(prodName)
System/CLOVA Studio Exclusive(VPC)
상품 키(cw_key)
1102262919682465792
성능/운영 지표

CLOVA Studio Exclusive 서비스의 성능/운영 지표는 다음과 같습니다.

Metric

Metric name	Data type	Unit	Metric type	Description	Interval	Aggregation
request_count	integer	num	Basic,Default	API request count	Min1, Min5, Min30, Hour2, Day1	AVG, SUM
response_count_2xx	integer	num	Basic,Default	API response count (Success)	Min1, Min5, Min30, Hour2, Day1	AVG, SUM
response_count_4xx	integer	num	Basic	API response count (4xx)	Min1, Min5, Min30, Hour2, Day1	AVG, SUM
response_count_5xx	integer	num	Basic,Default	API response count (5xx)	Min1, Min5, Min30, Hour2, Day1	AVG, SUM
average_latency	float	millisecond (avg)	Basic	Average latency per min.	Min1	AVG
input_token_usage	integer	num	Basic,Default	Input token usage	Min1, Min5, Min30, Hour2, Day1	AVG, SUM
output_token_usage	integer	num	Basic,Default	Output token usage	Min1, Min5, Min30, Hour2, Day1	AVG, SUM

Dimension

Dimension name	Data type
mbrNo	STRING
modelName	STRING
contractNo	STRING

---

# CLOVA Studio 릴리스 노트

## CLOVA Studio 릴리스 노트

원문: https://api.ncloud-docs.com/docs/clovastudio-releasenote

Classic/VPC 환경에서 이용 가능합니다.

CLOVA Studio API 가이드의 릴리스 노트입니다. 릴리스 내용은 다음과 같은 기준으로 구분하여 작성했습니다.

New
서비스 신규 출시
Update
기능 추가: 서비스의 신규 기능 추가
기능 변경: 서비스의 기능 변경
버그 개선: 서비스의 버그 개선
종료: 서비스 기능이나 서비스의 종료(fade-out)
기타: 서비스 업데이트와 무관한 가이드 내용 또는 구성의 변경

위 기준을 참고하여 릴리스 노트의 상세한 내용을 확인해 주십시오.

2025. 7. 29.
구분	변경 내용	상세 경로
Update - 기능 추가	HCX-007 추론 모델 제공	추론 (Thinking)
Update - 기능 추가	Structured Outputs 기능 제공
HCX-007 모델을 통해 JSON 형식의 출력 결과를 손쉽게 생성
	Structured Outputs
2025. 7. 17.
구분	변경 내용	상세 경로
Update - 기능 추가	익스플로러 신규 도구 제공
리랭커
RAG Reasoning
	
리랭커
RAG Reasoning

Update - 기능 변경	API 연동 및 이용 방식 간소화
테스트 앱을 생성하지 않고 발급한 API 키로 모든 기능 사용 가능
	API 키 발급
2025. 6. 16.
구분	변경 내용	상세 경로
Update - 기능 추가	Function calling 스트림 제공	Function calling
2025. 4. 17.
구분	변경 내용	상세 경로
Update - 기능 추가	Chat Completions v3 API 제공	
텍스트 및 이미지
Function calling

Update - 기능 추가	토큰 계산기(챗 v3) API 제공	토큰 계산기(챗 v3)
Update - 기능 추가	라우터 API 제공	라우터
Update - 기능 추가	오픈AI 호환 API 제공	오픈AI 호환성
2025. 1. 16.
구분	변경 내용	상세 경로
Update - 기능 추가	신규 API 인증 방식 (Bearer) 추가 지원 및 API 키 관리 기능 제공
기존 인증 방식 (Custom) 지속 이용 가능
	CLOVA Studio API 개요
Update - 기능 개선	HCX-003 모델의 context length 확대
입력 토큰과 출력 토큰의 합계 최대 8,192 토큰
입력 토큰 최대 7,600 토큰
모델에게 요청할 출력 토큰(maxTokens) 최대 4,096 토큰까지 설정 가능
	CLOVA Studio 개요
2024. 9. 26.
구분	변경 내용	상세 경로
Update - 기타	가이드 콘텐츠 보강 및 스타일 개선	CLOVA Studio 개요
2024. 6. 20.
구분	변경 내용	상세 경로
Update - 기타	가이드 구성 개편 및 콘텐츠 보강
익스플로러 API 명세 추가
문제 해결 추가
릴리스 노트 제공
	
토큰 계산기 API 명세
슬라이딩 윈도우 API 명세
문단 나누기 API 명세
요약 API 명세
임베딩 API 명세
CLOVA Studio 문제 해결
CLOVA Studio 릴리스 노트

---
