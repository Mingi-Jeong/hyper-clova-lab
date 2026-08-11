from pathlib import Path

import httpx2
import pytest
from pydantic import ValidationError

from hcx_eval.clients.base import ProviderApiError, RequestBudget, RequestPolicy
from hcx_eval.clients.openai_compat import OpenAICompatibleClient
from hcx_eval.registry.discovery import discover_models


@pytest.mark.anyio
async def test_discovery_saves_models_bytes_exactly(tmp_path: Path) -> None:
    # Given
    raw = b'{"object":"list", "data":[{"id":"HCX-NEW","object":"model"}]}'

    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            200,
            content=raw,
            headers={"content-type": "application/json"},
            request=request,
        )

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=1, max_tokens=1)),
        transport=httpx2.MockTransport(handler),
    )
    output = tmp_path / "models.raw.json"

    # When
    result = await discover_models(client=client, documented=(), raw_output=output)

    # Then
    assert output.read_bytes() == raw
    assert result.models[0].identifier == "HCX-NEW"
    assert result.external_requests == 1


@pytest.mark.anyio
async def test_discovery_preserves_malformed_models_before_parse(
    tmp_path: Path,
) -> None:
    # Given
    raw = b'{"object":"list","data":['

    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, content=raw, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=1, max_tokens=1)),
        transport=httpx2.MockTransport(handler),
    )
    output = tmp_path / "malformed.raw.json"

    # When / Then
    with pytest.raises(ValidationError):
        _ = await discover_models(client=client, documented=(), raw_output=output)
    assert output.read_bytes() == raw


@pytest.mark.anyio
async def test_discovery_preserves_non_success_models_before_classification(
    tmp_path: Path,
) -> None:
    # Given
    raw = b'{"status":{"code":"50000","message":"failed"}}'

    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(500, content=raw, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=1, max_tokens=1)),
        transport=httpx2.MockTransport(handler),
    )
    output = tmp_path / "error.raw.json"

    # When / Then
    with pytest.raises(ProviderApiError):
        _ = await discover_models(client=client, documented=(), raw_output=output)
    assert output.read_bytes() == raw
