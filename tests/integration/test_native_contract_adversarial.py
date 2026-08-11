import httpx2
import pytest
from pydantic import ValidationError

from hcx_eval.clients.base import RequestBudget, RequestPolicy
from hcx_eval.clients.native_v1 import NativeV1ChatRequest, NativeV1Client
from hcx_eval.clients.native_v3 import NativeV3ChatRequest, NativeV3Client
from hcx_eval.clients.types import ChatMessage


def enabled_budget() -> RequestBudget:
    return RequestBudget(
        RequestPolicy(
            execute=True,
            max_requests=2,
            max_tokens=100,
            max_retries=0,
        )
    )


@pytest.mark.anyio
async def test_native_parsers_reject_mixed_contract_responses() -> None:
    # Given
    mixed = {
        "status": {"code": "20000", "message": "OK"},
        "result": {
            "message": {"role": "assistant", "content": "wrong"},
            "stopReason": "end_token",
            "inputLength": 1,
            "outputLength": 1,
            "finishReason": "stop",
            "usage": {
                "promptTokens": 1,
                "completionTokens": 1,
                "totalTokens": 2,
            },
            "created": 1,
        },
    }

    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json=mixed, request=request)

    message = ChatMessage(role="user", content="hi")
    v1 = NativeV1Client(
        base_url="https://offline.invalid",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(handler),
    )
    v3 = NativeV3Client(
        base_url="https://offline.invalid",
        api_key="key",
        budget=enabled_budget(),
        transport=httpx2.MockTransport(handler),
    )

    # When / Then
    with pytest.raises(ValidationError):
        _ = await v1.chat(NativeV1ChatRequest(model="HCX-003", messages=(message,)))
    with pytest.raises(ValidationError):
        _ = await v3.chat(
            NativeV3ChatRequest(model="HCX-005", messages=(message,), max_tokens=4)
        )
