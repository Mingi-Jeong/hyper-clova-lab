import httpx2
import pytest
from pydantic import JsonValue, TypeAdapter

from hcx_eval.clients.base import (
    ErrorKind,
    ProviderApiError,
    RequestBudget,
    RequestPolicy,
)
from hcx_eval.clients.native_v1 import NativeV1ChatRequest, NativeV1Client
from hcx_eval.clients.native_v3 import NativeV3ChatRequest, NativeV3Client
from hcx_eval.clients.openai_compat import (
    OpenAIChatRequest,
    OpenAICompatibleClient,
    OpenAIEmbeddingRequest,
)
from hcx_eval.clients.types import ChatMessage

_JSON_OBJECT = TypeAdapter(dict[str, JsonValue])


def enabled_budget(*, requests: int = 10, retries: int = 0) -> RequestBudget:
    return RequestBudget(
        RequestPolicy(
            execute=True,
            max_requests=requests,
            max_tokens=100,
            max_retries=retries,
        )
    )


@pytest.mark.anyio
async def test_openai_adapter_uses_openai_wire_contracts() -> None:
    # Given
    seen: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        if request.url.path.endswith("/chat/completions"):
            return httpx2.Response(
                200,
                json={
                    "id": "chat-1",
                    "object": "chat.completion",
                    "created": 1,
                    "model": "HCX-005",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "ok"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 2,
                        "completion_tokens": 1,
                        "total_tokens": 3,
                    },
                },
                request=request,
            )
        return httpx2.Response(
            200,
            json={
                "object": "list",
                "data": [{"object": "embedding", "index": 0, "embedding": [0.1]}],
                "model": "bge-m3",
                "usage": {"prompt_tokens": 1, "total_tokens": 1},
            },
            request=request,
        )

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(handler),
    )

    # When
    chat = await client.chat(
        OpenAIChatRequest(
            model="HCX-005",
            messages=(ChatMessage(role="user", content="hi"),),
            max_tokens=4,
        )
    )
    embedding = await client.embed(OpenAIEmbeddingRequest(model="bge-m3", input="hi"))

    # Then
    assert chat.choices[0].message.content == "ok"
    assert embedding.data[0].embedding == (0.1,)
    chat_body = _JSON_OBJECT.validate_json(seen[0].content)
    embedding_body = _JSON_OBJECT.validate_json(seen[1].content)
    assert seen[0].url.path == "/v1/openai/chat/completions"
    assert chat_body["max_tokens"] == 4
    assert "maxTokens" not in chat_body
    assert embedding_body["encoding_format"] == "float"
    assert seen[0].headers["authorization"] == "Bearer key"


@pytest.mark.anyio
async def test_native_v1_and_v3_keep_field_and_response_differences() -> None:
    # Given
    seen: list[httpx2.Request] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        if "/v1/" in request.url.path:
            payload = {
                "status": {"code": "20000", "message": "OK"},
                "result": {
                    "message": {"role": "assistant", "content": "v1"},
                    "stopReason": "end_token",
                    "inputLength": 2,
                    "outputLength": 1,
                },
            }
        else:
            payload = {
                "status": {"code": "20000", "message": "OK"},
                "result": {
                    "message": {"role": "assistant", "content": "v3"},
                    "finishReason": "stop",
                    "usage": {
                        "promptTokens": 2,
                        "completionTokens": 1,
                        "totalTokens": 3,
                    },
                    "created": 1,
                },
            }
        return httpx2.Response(200, json=payload, request=request)

    transport = httpx2.MockTransport(handler)
    v1 = NativeV1Client(
        base_url="https://offline.invalid",
        api_key="key",
        budget=enabled_budget(),
        transport=transport,
    )
    v3 = NativeV3Client(
        base_url="https://offline.invalid",
        api_key="key",
        budget=enabled_budget(),
        transport=transport,
    )
    message = ChatMessage(role="user", content="hi")

    # When
    one = await v1.chat(
        NativeV1ChatRequest(
            model="HCX-003",
            messages=(message,),
            max_tokens=4,
            repeat_penalty=5.0,
            stop_before=("x",),
        )
    )
    three = await v3.chat(
        NativeV3ChatRequest(
            model="HCX-005",
            messages=(message,),
            max_tokens=4,
            repetition_penalty=1.1,
            stop=("x",),
        )
    )

    # Then
    assert one.result.input_length == 2
    assert three.result.usage.total_tokens == 3
    v1_body = _JSON_OBJECT.validate_json(seen[0].content)
    v3_body = _JSON_OBJECT.validate_json(seen[1].content)
    assert v1_body["repeatPenalty"] == 5.0
    assert v1_body["stopBefore"] == ["x"]
    assert v3_body["repetitionPenalty"] == 1.1
    assert v3_body["stop"] == ["x"]
    assert seen[0].url.path == "/v1/chat-completions/HCX-003"
    assert seen[1].url.path == "/v3/chat-completions/HCX-005"


@pytest.mark.anyio
async def test_retry_ceiling_and_provider_error_are_preserved() -> None:
    # Given
    calls = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        return httpx2.Response(
            429,
            headers={"Retry-After": "0"},
            json={"status": {"code": "42902", "message": "overloaded"}},
            request=request,
        )

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=enabled_budget(retries=1),
        transport=httpx2.MockTransport(handler),
    )

    # When / Then
    with pytest.raises(ProviderApiError) as captured:
        _ = await client.list_models()
    assert calls == 2
    assert captured.value.http_status == 429
    assert captured.value.provider_code == "42902"
    assert captured.value.retry_after == "0"


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("status", "code", "kind"),
    [(401, "40104", ErrorKind.AUTHENTICATION), (500, "50000", ErrorKind.SERVER)],
)
async def test_provider_status_classification(
    status: int, code: str, kind: ErrorKind
) -> None:
    # Given
    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            status,
            json={"status": {"code": code, "message": "safe"}},
            request=request,
        )

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(handler),
    )

    # When / Then
    with pytest.raises(ProviderApiError) as captured:
        _ = await client.list_models()
    assert captured.value.kind is kind
    assert captured.value.provider_code == code


@pytest.mark.anyio
async def test_transport_timeout_is_preserved_without_secret() -> None:
    # Given
    async def handler(request: httpx2.Request) -> httpx2.Response:
        message = "secret body"
        raise httpx2.ReadTimeout(message, request=request)

    client = OpenAICompatibleClient(
        base_url="https://user:pass@offline.invalid/v1/openai?api_key=secret",
        api_key="secret",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(handler),
    )

    # When / Then
    with pytest.raises(ProviderApiError) as captured:
        _ = await client.list_models()
    assert captured.value.kind is ErrorKind.TIMEOUT
    assert "secret" not in str(captured.value)


@pytest.mark.anyio
async def test_native_stream_sets_accept_and_parses_content() -> None:
    # Given
    seen: list[httpx2.Request] = []
    raw = b'event: token\ndata: {"message":{"content":"hi"}}\n\n'

    async def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(200, content=raw, request=request)

    client = NativeV3Client(
        base_url="https://offline.invalid",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(handler),
    )

    # When
    parsed = await client.chat_stream(
        NativeV3ChatRequest(
            model="HCX-005",
            messages=(ChatMessage(role="user", content="hi"),),
            max_tokens=4,
        )
    )

    # Then
    assert seen[0].headers["accept"] == "text/event-stream"
    assert parsed.events[0].content == "hi"
