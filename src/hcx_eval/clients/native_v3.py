"""Native v3 Chat Completions adapter."""

from typing import ClassVar

import httpx2
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from hcx_eval.clients.base import HttpExecutor, RequestBudget, create_async_client
from hcx_eval.clients.sse import ParsedStream, parse_sse
from hcx_eval.clients.types import ChatMessage


class NativeV3ChatRequest(BaseModel):
    """Native v3 request with current field names."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    model: str
    messages: tuple[ChatMessage, ...]
    max_tokens: int = Field(default=512, ge=1)
    repetition_penalty: float = Field(default=1.1, gt=0, le=2)
    stop: tuple[str, ...] = ()

    def wire_body(self) -> dict[str, JsonValue]:
        """Serialize only documented native v3 names."""
        return {
            "messages": [
                {"role": message.role, "content": message.content}
                for message in self.messages
            ],
            "maxTokens": self.max_tokens,
            "repetitionPenalty": self.repetition_penalty,
            "stop": list(self.stop),
        }


class NativeV3Usage(BaseModel):
    """Native v3 camelCase token usage."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    prompt_tokens: int = Field(validation_alias="promptTokens")
    completion_tokens: int = Field(validation_alias="completionTokens")
    total_tokens: int = Field(validation_alias="totalTokens")


class NativeV3Result(BaseModel):
    """Native v3 result with finish reason and usage."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    message: ChatMessage
    finish_reason: str = Field(validation_alias="finishReason")
    usage: NativeV3Usage
    created: int


class NativeV3Response(BaseModel):
    """Validated native v3 response envelope."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    result: NativeV3Result


class NativeV3Client:
    """Wire-injectable native v3 client."""

    _executor: HttpExecutor

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        budget: RequestBudget,
        transport: httpx2.AsyncBaseTransport | None = None,
    ) -> None:
        """Bind the native v3 endpoint to bounded execution."""
        self._executor = HttpExecutor(
            client=create_async_client(
                base_url=base_url, api_key=api_key, transport=transport
            ),
            budget=budget,
        )

    async def chat(self, request: NativeV3ChatRequest) -> NativeV3Response:
        """Generate through `/v3/chat-completions/{model}`."""
        response = await self._executor.request(
            method="POST",
            path=f"v3/chat-completions/{request.model}",
            estimated_tokens=request.max_tokens,
            json_body=request.wire_body(),
        )
        return NativeV3Response.model_validate_json(response.content)

    async def chat_stream(self, request: NativeV3ChatRequest) -> ParsedStream:
        """Parse a native v3 SSE chat stream."""
        response = await self._executor.request(
            method="POST",
            path=f"v3/chat-completions/{request.model}",
            estimated_tokens=request.max_tokens,
            json_body=request.wire_body(),
            headers={"Accept": "text/event-stream"},
        )
        return parse_sse(response.content)
