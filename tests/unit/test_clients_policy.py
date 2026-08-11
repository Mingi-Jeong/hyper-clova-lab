import httpx2
import pytest

from hcx_eval.clients.base import (
    ApiFamily,
    BudgetExceededError,
    ExecutionDisabledError,
    RequestBudget,
    RequestPolicy,
)
from hcx_eval.clients.openai_compat import OpenAIChatRequest, OpenAICompatibleClient
from hcx_eval.clients.types import ChatMessage


@pytest.mark.anyio
async def test_request_is_blocked_when_execution_is_disabled() -> None:
    # Given
    calls = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        return httpx2.Response(200, json={"data": []}, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="secret",
        budget=RequestBudget(
            RequestPolicy(execute=False, max_requests=1, max_tokens=1)
        ),
        transport=httpx2.MockTransport(handler),
    )

    # When / Then
    with pytest.raises(ExecutionDisabledError):
        _ = await client.list_models()
    assert calls == 0


@pytest.mark.anyio
async def test_request_ceiling_is_enforced_before_second_dispatch() -> None:
    # Given
    calls = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        return httpx2.Response(200, json={"data": []}, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="secret",
        budget=RequestBudget(
            RequestPolicy(execute=True, max_requests=1, max_tokens=10)
        ),
        transport=httpx2.MockTransport(handler),
    )
    _ = await client.list_models()

    # When / Then
    with pytest.raises(BudgetExceededError):
        _ = await client.list_models()
    assert calls == 1


def test_dry_run_plan_has_sanitized_endpoint_and_contract() -> None:
    # Given
    client = OpenAICompatibleClient(
        base_url="https://user:pass@offline.invalid/v1/openai?api_key=secret",
        api_key="secret",
        budget=RequestBudget(
            RequestPolicy(execute=False, max_requests=0, max_tokens=0)
        ),
        transport=httpx2.MockTransport(lambda request: httpx2.Response(500)),
    )

    # When
    plan = client.plan_models()

    # Then
    assert plan.endpoint == "https://offline.invalid/v1/openai/models"
    assert plan.api_family is ApiFamily.OPENAI_COMPATIBLE
    assert "secret" not in plan.model_dump_json()


@pytest.mark.anyio
async def test_token_ceiling_is_enforced_before_dispatch() -> None:
    # Given
    calls = 0

    async def handler(request: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        return httpx2.Response(200, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="secret",
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=1, max_tokens=3)),
        transport=httpx2.MockTransport(handler),
    )

    # When / Then
    with pytest.raises(BudgetExceededError):
        _ = await client.chat(
            OpenAIChatRequest(
                model="HCX-005",
                messages=(ChatMessage(role="user", content="hi"),),
                max_tokens=4,
            )
        )
    assert calls == 0
