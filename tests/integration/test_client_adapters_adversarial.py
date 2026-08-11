from __future__ import annotations

from typing import TYPE_CHECKING

import httpx2
import pytest
from pydantic import JsonValue, TypeAdapter, ValidationError
from typing_extensions import override

from hcx_eval.clients.base import (
    ErrorKind,
    ProviderApiError,
    RequestBudget,
    RequestPolicy,
)
from hcx_eval.clients.executor import HttpExecutor
from hcx_eval.clients.native_v1 import NativeV1ChatRequest, NativeV1Client
from hcx_eval.clients.native_v3 import NativeV3ChatRequest, NativeV3Client
from hcx_eval.clients.openai_compat import (
    OpenAIChatRequest,
    OpenAICompatibleClient,
    OpenAIEmbeddingRequest,
)
from hcx_eval.clients.types import ChatMessage

_JSON_OBJECT = TypeAdapter(dict[str, JsonValue])

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator


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
async def test_models_accept_numeric_openai_metadata() -> None:
    # Given
    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            200,
            json={
                "object": "list",
                "data": [
                    {
                        "id": "HCX-005",
                        "object": "model",
                        "created": 123,
                        "owned_by": "naver",
                    }
                ],
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
    result = await client.list_models()

    # Then
    assert result.models == ("HCX-005",)


@pytest.mark.anyio
async def test_openai_stream_uses_stream_flag_and_parses_delta() -> None:
    # Given
    seen: list[httpx2.Request] = []
    raw = (
        b'data: {"choices":[{"delta":{"content":""}}]}\n\n'
        b'data: {"choices":[{"delta":{"content":"hello"}}]}\n\n'
        b"data: [DONE]\n\n"
    )

    async def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(200, content=raw, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(handler),
    )

    # When
    parsed = await client.chat_stream(
        OpenAIChatRequest(
            model="HCX-005",
            messages=(ChatMessage(role="user", content="hi"),),
            max_tokens=4,
        )
    )

    # Then
    body = _JSON_OBJECT.validate_json(seen[0].content)
    assert body["stream"] is True
    assert seen[0].headers["accept"] == "text/event-stream"
    assert parsed.first_content_at is not None
    assert parsed.events[1].content == "hello"


def test_embedding_rejects_base64_encoding_at_boundary() -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = OpenAIEmbeddingRequest.model_validate(
            {"model": "bge-m3", "input": "text", "encoding_format": "base64"}
        )


@pytest.mark.anyio
async def test_retry_after_and_backoff_use_injected_timing() -> None:
    # Given
    responses: Iterator[tuple[int, dict[str, str]]] = iter(
        (
            (429, {"Retry-After": "2"}),
            (500, dict[str, str]()),
            (200, dict[str, str]()),
        )
    )
    delays: list[float] = []

    async def handler(request: httpx2.Request) -> httpx2.Response:
        status, headers = next(responses)
        return httpx2.Response(
            status,
            headers=headers,
            json={"status": {"code": str(status), "message": "state"}},
            request=request,
        )

    async def sleep(delay_seconds: float) -> None:
        delays.append(delay_seconds)

    wire = httpx2.AsyncClient(
        base_url="https://offline.invalid",
        transport=httpx2.MockTransport(handler),
    )
    executor = HttpExecutor(
        client=wire,
        budget=RequestBudget(
            RequestPolicy(
                execute=True,
                max_requests=3,
                max_tokens=1,
                max_retries=2,
            )
        ),
        retry_sleep=sleep,
    )

    # When
    response = await executor.request(method="GET", path="models")

    # Then
    assert response.status_code == 200
    assert delays == [2.0, 2.0]


@pytest.mark.anyio
async def test_native_parsers_reject_cross_contract_responses() -> None:
    # Given
    v3_response = {
        "status": {"code": "20000", "message": "OK"},
        "result": {
            "message": {"role": "assistant", "content": "wrong"},
            "finishReason": "stop",
            "usage": {
                "promptTokens": 1,
                "completionTokens": 1,
                "totalTokens": 2,
            },
            "created": 1,
        },
    }
    v1_response = {
        "status": {"code": "20000", "message": "OK"},
        "result": {
            "message": {"role": "assistant", "content": "wrong"},
            "stopReason": "end_token",
            "inputLength": 1,
            "outputLength": 1,
        },
    }

    async def v3_handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json=v3_response, request=request)

    async def v1_handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json=v1_response, request=request)

    message = ChatMessage(role="user", content="hi")
    v1 = NativeV1Client(
        base_url="https://offline.invalid",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(v3_handler),
    )
    v3 = NativeV3Client(
        base_url="https://offline.invalid",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(v1_handler),
    )

    # When / Then
    with pytest.raises(ValidationError):
        _ = await v1.chat(NativeV1ChatRequest(model="HCX-003", messages=(message,)))
    with pytest.raises(ValidationError):
        _ = await v3.chat(
            NativeV3ChatRequest(model="HCX-005", messages=(message,), max_tokens=4)
        )


def test_native_requests_reject_cross_contract_body_fields() -> None:
    # Given
    message = ChatMessage(role="user", content="hi")

    # When / Then
    with pytest.raises(ValidationError):
        _ = NativeV1ChatRequest.model_validate(
            {
                "model": "HCX-003",
                "messages": [message.model_dump()],
                "repetition_penalty": 1.1,
            }
        )
    with pytest.raises(ValidationError):
        _ = NativeV3ChatRequest.model_validate(
            {
                "model": "HCX-005",
                "messages": [message.model_dump()],
                "repeat_penalty": 5.0,
            }
        )


@pytest.mark.anyio
async def test_malformed_openai_success_payload_is_rejected() -> None:
    # Given
    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            200,
            json={"id": "bad", "model": "HCX-005", "choices": []},
            request=request,
        )

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(handler),
    )

    # When / Then
    with pytest.raises(ValidationError):
        _ = await client.chat(
            OpenAIChatRequest(
                model="HCX-005",
                messages=(ChatMessage(role="user", content="hi"),),
                max_tokens=4,
            )
        )


@pytest.mark.anyio
async def test_partial_stream_timeout_is_not_retried() -> None:
    # Given
    calls = 0

    class PartialTimeoutStream(httpx2.AsyncByteStream):
        @override
        async def __aiter__(self) -> AsyncIterator[bytes]:
            yield b'data: {"choices":[{"delta":{"content":"partial"}}]}\n\n'
            message = "stream stalled"
            raise httpx2.ReadTimeout(message)

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        return httpx2.Response(200, stream=PartialTimeoutStream(), request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=enabled_budget(retries=1),
        transport=httpx2.MockTransport(handler),
    )

    # When / Then
    with pytest.raises(ProviderApiError) as captured:
        _ = await client.chat_stream(
            OpenAIChatRequest(
                model="HCX-005",
                messages=(ChatMessage(role="user", content="hi"),),
                max_tokens=4,
            )
        )
    assert captured.value.kind is ErrorKind.TIMEOUT
    assert calls == 1
