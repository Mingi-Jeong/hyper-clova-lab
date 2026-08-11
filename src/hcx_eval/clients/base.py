"""Shared execution budget, retry policy, and sanitized HTTP errors."""

from __future__ import annotations

import socket
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar
from urllib.parse import urlsplit, urlunsplit

import httpx2
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import override

_CLIENT_ERROR = 400
_SERVER_ERROR = 500
_RATE_LIMIT = 429


class ApiFamily(StrEnum):
    """Distinct provider wire contract."""

    OPENAI_COMPATIBLE = "openai-compatible"
    NATIVE_V1 = "native-v1"
    NATIVE_V3 = "native-v3"


class ErrorKind(StrEnum):
    """Stable transport/provider error classification."""

    AUTHENTICATION = "authentication"
    INVALID_REQUEST = "invalid-request"
    RATE_LIMIT = "rate-limit"
    SERVER = "server"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class RequestPolicy(BaseModel):
    """One bounded execution authorization."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    execute: bool = False
    max_requests: int = Field(ge=0)
    max_tokens: int = Field(ge=0)
    max_retries: int = Field(default=0, ge=0, le=10)


class RequestPlan(BaseModel):
    """Secret-free plan suitable for dry-run output."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    api_family: ApiFamily
    method: str
    endpoint: str
    model: str | None = None
    estimated_tokens: int = Field(ge=0)


@dataclass(frozen=True, slots=True)
class ExecutionDisabledError(RuntimeError):
    """A network dispatch was attempted without explicit execution approval."""

    @override
    def __str__(self) -> str:
        """Render the fixed safe failure."""
        return "network execution is disabled"


@dataclass(frozen=True, slots=True)
class BudgetExceededError(RuntimeError):
    """A request or token ceiling would be exceeded."""

    resource: str
    limit: int

    @override
    def __str__(self) -> str:
        return f"{self.resource} budget exhausted at {self.limit}"


@dataclass(frozen=True, slots=True)
class ProviderApiError(RuntimeError):
    """A sanitized provider or transport failure."""

    kind: ErrorKind
    endpoint: str
    http_status: int | None = None
    provider_code: str | None = None
    retry_after: str | None = None

    @override
    def __str__(self) -> str:
        status = "transport" if self.http_status is None else str(self.http_status)
        code = "unknown" if self.provider_code is None else self.provider_code
        return (
            f"provider request failed ({self.kind}, HTTP {status}, "
            f"code {code}) at {self.endpoint}"
        )


class RequestBudget:
    """Mutable per-run accounting state shared by all adapter instances."""

    __slots__: ClassVar[tuple[str, ...]] = ("_requests", "_tokens", "policy")
    policy: RequestPolicy
    _requests: int
    _tokens: int

    def __init__(self, policy: RequestPolicy) -> None:
        """Initialize zeroed accounting for one policy."""
        self.policy = policy
        self._requests = 0
        self._tokens = 0

    @property
    def requests_used(self) -> int:
        """Return dispatched attempts, including retries."""
        return self._requests

    def reserve(self, estimated_tokens: int) -> None:
        """Reserve one attempt before it reaches the transport."""
        if not self.policy.execute:
            raise ExecutionDisabledError
        if self.policy.max_requests <= 0 or self._requests >= self.policy.max_requests:
            raise BudgetExceededError(
                resource="request", limit=self.policy.max_requests
            )
        if (
            self.policy.max_tokens <= 0
            or self._tokens + estimated_tokens > self.policy.max_tokens
        ):
            raise BudgetExceededError(resource="token", limit=self.policy.max_tokens)
        self._requests += 1
        self._tokens += estimated_tokens


def sanitized_url(url: str) -> str:
    """Remove credentials, query, and fragment from an endpoint."""
    parts = urlsplit(url)
    hostname = parts.hostname or "invalid"
    port = "" if parts.port is None else f":{parts.port}"
    return urlunsplit(
        (parts.scheme, f"{hostname}{port}", parts.path.rstrip("/"), "", "")
    )


def create_async_client(
    *,
    base_url: str,
    api_key: str,
    transport: httpx2.AsyncBaseTransport | None = None,
) -> httpx2.AsyncClient:
    """Create an optimized client with transport retries disabled for policy control."""
    selected_transport = transport or httpx2.AsyncHTTPTransport(
        http2=True,
        retries=0,
        limits=httpx2.Limits(
            max_connections=200,
            max_keepalive_connections=40,
            keepalive_expiry=30.0,
        ),
        socket_options=[(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)],
    )
    return httpx2.AsyncClient(
        base_url=sanitized_url(base_url),
        headers={"Authorization": f"Bearer {api_key}"},
        transport=selected_transport,
        timeout=httpx2.Timeout(connect=5.0, read=30.0, write=10.0, pool=10.0),
        follow_redirects=True,
        trust_env=False,
    )


def classify_status(status: int) -> ErrorKind:
    """Map HTTP status to a stable error category."""
    if status in {401, 403}:
        return ErrorKind.AUTHENTICATION
    if status in {408, 504}:
        return ErrorKind.TIMEOUT
    if status == _RATE_LIMIT:
        return ErrorKind.RATE_LIMIT
    if _CLIENT_ERROR <= status < _SERVER_ERROR:
        return ErrorKind.INVALID_REQUEST
    if status >= _SERVER_ERROR:
        return ErrorKind.SERVER
    return ErrorKind.UNKNOWN
