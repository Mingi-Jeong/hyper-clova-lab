"""Budgeted buffered and incremental HTTP execution."""

from typing import ClassVar, Final, Protocol

import anyio
import httpx2
from pydantic import BaseModel, ConfigDict, JsonValue

from hcx_eval.clients.base import (
    ErrorKind,
    ProviderApiError,
    RequestBudget,
    classify_status,
    sanitized_url,
)
from hcx_eval.clients.sse import ParsedStream, parse_sse_lines
from hcx_eval.security import redact_bytes, redact_text

_CLIENT_ERROR: Final = 400
_RETRY_BACKOFF_SECONDS: Final[float] = 1.0
_MAX_RETRY_DELAY_SECONDS: Final[float] = 60.0


class _ProviderStatus(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    code: str
    message: str


class _NativeError(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    status: _ProviderStatus


class _CompatibleError(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    error: _ProviderStatus


def _error_details(response: httpx2.Response) -> str | None:
    try:
        native = _NativeError.model_validate_json(response.content)
    except ValueError:
        try:
            compatible = _CompatibleError.model_validate_json(response.content)
        except ValueError:
            return None
        else:
            return redact_text(compatible.error.code)
    else:
        return redact_text(native.status.code)


def _provider_error(response: httpx2.Response, endpoint: str) -> ProviderApiError:
    return ProviderApiError(
        kind=classify_status(response.status_code),
        endpoint=endpoint,
        http_status=response.status_code,
        provider_code=_error_details(response),
        retry_after=response.headers.get("Retry-After"),
        response_body=redact_bytes(response.content),
    )


def _retryable(error: ProviderApiError) -> bool:
    return error.kind in {
        ErrorKind.RATE_LIMIT,
        ErrorKind.SERVER,
        ErrorKind.TIMEOUT,
    }


class RetrySleep(Protocol):
    """Injectable retry wait boundary."""

    async def __call__(self, delay_seconds: float) -> None:
        """Wait for the chosen retry delay."""
        ...


async def _default_retry_sleep(delay_seconds: float) -> None:
    await anyio.sleep(delay_seconds)


def _retry_delay(retry_after: str | None, attempt: int) -> float:
    fallback = _RETRY_BACKOFF_SECONDS * (2.0**attempt)
    if retry_after is None:
        return min(fallback, _MAX_RETRY_DELAY_SECONDS)
    try:
        requested = float(retry_after)
    except ValueError:
        return min(fallback, _MAX_RETRY_DELAY_SECONDS)
    return min(max(requested, 0.0), _MAX_RETRY_DELAY_SECONDS)


class HttpExecutor:
    """HTTP execution seam shared by all concrete adapters."""

    _client: httpx2.AsyncClient
    _budget: RequestBudget
    _retry_sleep: RetrySleep

    def __init__(
        self,
        *,
        client: httpx2.AsyncClient,
        budget: RequestBudget,
        retry_sleep: RetrySleep = _default_retry_sleep,
    ) -> None:
        """Bind a configured client to shared run accounting."""
        self._client = client
        self._budget = budget
        self._retry_sleep = retry_sleep

    async def request(
        self,
        *,
        method: str,
        path: str,
        estimated_tokens: int = 0,
        json_body: JsonValue | None = None,
    ) -> httpx2.Response:
        """Dispatch a buffered request within aggregate ceilings."""
        attempts = self._budget.policy.max_retries + 1
        endpoint = sanitized_url(str(self._client.base_url.join(path)))
        for attempt in range(attempts):
            self._budget.reserve(estimated_tokens if attempt == 0 else 0)
            try:
                response = await self._client.request(method, path, json=json_body)
                if response.status_code < _CLIENT_ERROR:
                    return response
                error = _provider_error(response, endpoint)
                if _retryable(error) and attempt + 1 < attempts:
                    await self._retry_sleep(_retry_delay(error.retry_after, attempt))
                    continue
                raise error
            except httpx2.TimeoutException as error:
                if attempt + 1 < attempts:
                    delay = _RETRY_BACKOFF_SECONDS * (2.0**attempt)
                    await self._retry_sleep(min(delay, _MAX_RETRY_DELAY_SECONDS))
                    continue
                raise ProviderApiError(
                    kind=ErrorKind.TIMEOUT, endpoint=endpoint
                ) from error
        raise AssertionError

    async def stream(
        self, *, path: str, estimated_tokens: int, json_body: JsonValue
    ) -> ParsedStream:
        """Consume SSE blocks incrementally within aggregate ceilings."""
        attempts = self._budget.policy.max_retries + 1
        endpoint = sanitized_url(str(self._client.base_url.join(path)))
        for attempt in range(attempts):
            self._budget.reserve(estimated_tokens if attempt == 0 else 0)
            request = self._client.build_request(
                "POST",
                path,
                json=json_body,
                headers={"Accept": "text/event-stream"},
            )
            try:
                response = await self._client.send(request, stream=True)
            except httpx2.TimeoutException as error:
                if attempt + 1 < attempts:
                    delay = _RETRY_BACKOFF_SECONDS * (2.0**attempt)
                    await self._retry_sleep(min(delay, _MAX_RETRY_DELAY_SECONDS))
                    continue
                raise ProviderApiError(
                    kind=ErrorKind.TIMEOUT, endpoint=endpoint
                ) from error
            try:
                if response.status_code >= _CLIENT_ERROR:
                    _ = await response.aread()
                    error = _provider_error(response, endpoint)
                    if _retryable(error) and attempt + 1 < attempts:
                        await self._retry_sleep(
                            _retry_delay(error.retry_after, attempt)
                        )
                        continue
                    raise error
                try:
                    return await parse_sse_lines(response.aiter_lines())
                except httpx2.TimeoutException as error:
                    raise ProviderApiError(
                        kind=ErrorKind.TIMEOUT, endpoint=endpoint
                    ) from error
            finally:
                await response.aclose()
        raise AssertionError
