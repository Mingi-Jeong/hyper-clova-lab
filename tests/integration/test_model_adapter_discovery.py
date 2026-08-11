from pathlib import Path

import httpx2
import pytest
from pydantic import ValidationError

from hcx_eval.clients.base import ProviderApiError, RequestBudget, RequestPolicy
from hcx_eval.clients.openai_compat import OpenAICompatibleClient
from hcx_eval.registry.discovery import discover_models, write_model_registry
from hcx_eval.schemas.model import ModelRecord, ModelStatus


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


@pytest.mark.anyio
async def test_discovery_redacts_sensitive_non_success_evidence(
    tmp_path: Path,
) -> None:
    # Given
    raw = (
        b"api_key=provider-reflected-key\n"
        b"Authorization: Bearer reflected-bearer\n"
        b"Cookie: session=reflected-cookie\n"
    )

    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(500, content=raw, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=1, max_tokens=1)),
        transport=httpx2.MockTransport(handler),
    )
    output = tmp_path / "error.sanitized.txt"

    # When / Then
    with pytest.raises(ProviderApiError) as captured:
        _ = await discover_models(client=client, documented=(), raw_output=output)
    persisted = output.read_bytes()
    assert persisted == captured.value.response_body
    assert b"provider-reflected-key" not in persisted
    assert b"reflected-bearer" not in persisted
    assert b"reflected-cookie" not in persisted
    assert b"[REDACTED]" in persisted


@pytest.mark.anyio
async def test_discovery_redacts_sensitive_malformed_success_evidence(
    tmp_path: Path,
) -> None:
    # Given
    raw = (
        b'{"api_key":"malformed-key",'
        b'"authorization":"Bearer malformed-bearer",'
        b'"cookie":"session=malformed-cookie",'
    )

    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, content=raw, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="key",
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=1, max_tokens=1)),
        transport=httpx2.MockTransport(handler),
    )
    output = tmp_path / "malformed.sanitized.txt"

    # When / Then
    with pytest.raises(ValidationError) as captured:
        _ = await discover_models(client=client, documented=(), raw_output=output)
    persisted = output.read_bytes()
    rendered_error = str(captured.value)
    assert b"malformed-key" not in persisted
    assert b"malformed-bearer" not in persisted
    assert b"malformed-cookie" not in persisted
    assert "malformed-key" not in rendered_error
    assert "malformed-bearer" not in rendered_error
    assert "malformed-cookie" not in rendered_error
    assert b"[REDACTED]" in persisted


def test_registry_writer_rejects_protected_source_target(tmp_path: Path) -> None:
    protected = tmp_path / "processed-data" / "registry.json"
    model = ModelRecord(
        identifier="HCX-MOCK",
        status=ModelStatus.LIVE,
        evidence=("fixture",),
    )

    with pytest.raises(ValueError, match="protected source root"):
        _ = write_model_registry((model,), protected)

    assert not protected.exists()
