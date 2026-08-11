"""OpenAI-compatible CLOVA Studio adapter."""

from typing import ClassVar, Literal

import httpx2
from pydantic import BaseModel, ConfigDict, Field

from hcx_eval.clients.base import (
    ApiFamily,
    RequestBudget,
    RequestPlan,
    create_async_client,
    sanitized_url,
)
from hcx_eval.clients.executor import HttpExecutor
from hcx_eval.clients.sse import ParsedStream
from hcx_eval.clients.types import ChatMessage


class OpenAIChatRequest(BaseModel):
    """OpenAI snake_case chat request."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    model: str
    messages: tuple[ChatMessage, ...]
    max_tokens: int | None = Field(default=None, ge=1)
    stream: bool = False


class OpenAIEmbeddingRequest(BaseModel):
    """OpenAI-compatible embedding request with mandatory float encoding."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    model: str
    input: str
    encoding_format: Literal["float"] = "float"


class OpenAIChoice(BaseModel):
    """One OpenAI-compatible chat choice."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    index: int
    message: ChatMessage
    finish_reason: str | None


class OpenAIUsage(BaseModel):
    """OpenAI snake_case token accounting."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    prompt_tokens: int
    completion_tokens: int = 0
    total_tokens: int


class OpenAIChatResponse(BaseModel):
    """OpenAI-compatible chat response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    id: str
    model: str
    choices: tuple[OpenAIChoice, ...]
    usage: OpenAIUsage


class OpenAIEmbeddingItem(BaseModel):
    """One OpenAI-compatible embedding vector."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    index: int
    embedding: tuple[float, ...]


class OpenAIEmbeddingResponse(BaseModel):
    """OpenAI-compatible embeddings response."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    data: tuple[OpenAIEmbeddingItem, ...]
    model: str
    usage: OpenAIUsage


class ModelListItem(BaseModel):
    """One heterogeneous OpenAI-compatible model descriptor."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    id: str
    object: str | None = None
    created: int | None = None
    owned_by: str | None = None


class ModelsWireResponse(BaseModel):
    """Untrusted `/models` response boundary."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    data: tuple[ModelListItem, ...]


class ModelsResponse(BaseModel):
    """Exact bytes and normalized identifiers from `/models`."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    raw: bytes
    models: tuple[str, ...]


class OpenAICompatibleClient:
    """Typed adapter for `/v1/openai` without SDK retry ambiguity."""

    _base_url: str
    _executor: HttpExecutor

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        budget: RequestBudget,
        transport: httpx2.AsyncBaseTransport | None = None,
    ) -> None:
        """Bind the compatible endpoint to bounded execution."""
        self._base_url = sanitized_url(base_url)
        self._executor = HttpExecutor(
            client=create_async_client(
                base_url=base_url, api_key=api_key, transport=transport
            ),
            budget=budget,
        )

    def plan_models(self) -> RequestPlan:
        """Build a secret-free model discovery plan."""
        return RequestPlan(
            api_family=ApiFamily.OPENAI_COMPATIBLE,
            method="GET",
            endpoint=f"{self._base_url}/models",
            estimated_tokens=0,
        )

    async def list_models(self) -> ModelsResponse:
        """Fetch model identifiers while retaining exact response bytes."""
        raw = await self.fetch_models_raw()
        return self.parse_models(raw)

    async def fetch_models_raw(self) -> bytes:
        """Acquire `/models` bytes without parsing the success payload."""
        response = await self._executor.request(method="GET", path="models")
        return response.content

    def parse_models(self, raw: bytes) -> ModelsResponse:
        """Parse identifiers from previously preserved `/models` bytes."""
        parsed = ModelsWireResponse.model_validate_json(raw)
        return ModelsResponse(raw=raw, models=tuple(item.id for item in parsed.data))

    async def chat(self, request: OpenAIChatRequest) -> OpenAIChatResponse:
        """Send an OpenAI-compatible chat request."""
        response = await self._executor.request(
            method="POST",
            path="chat/completions",
            estimated_tokens=request.max_tokens or 0,
            json_body=request.model_dump(exclude_none=True),
        )
        return OpenAIChatResponse.model_validate_json(response.content)

    async def embed(self, request: OpenAIEmbeddingRequest) -> OpenAIEmbeddingResponse:
        """Send an OpenAI-compatible float embedding request."""
        response = await self._executor.request(
            method="POST", path="embeddings", json_body=request.model_dump()
        )
        return OpenAIEmbeddingResponse.model_validate_json(response.content)

    async def chat_stream(self, request: OpenAIChatRequest) -> ParsedStream:
        """Parse an OpenAI-compatible SSE chat stream."""
        streaming_request = request.model_copy(update={"stream": True})
        return await self._executor.stream(
            path="chat/completions",
            estimated_tokens=request.max_tokens or 0,
            json_body=streaming_request.model_dump(exclude_none=True),
        )
