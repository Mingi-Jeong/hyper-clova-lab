"""Native v1 Chat Completions adapter."""

from typing import ClassVar

import httpx2
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, JsonValue

from hcx_eval.clients.base import HttpExecutor, RequestBudget, create_async_client
from hcx_eval.clients.sse import ParsedStream, parse_sse
from hcx_eval.clients.types import ChatMessage


class NativeV1ChatRequest(BaseModel):
    """Native v1 request with legacy field names."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
    model: str
    messages: tuple[ChatMessage, ...]
    max_tokens: int = Field(default=100, ge=1, le=4096)
    repeat_penalty: float = Field(default=5.0, gt=0, le=10)
    stop_before: tuple[str, ...] = ()

    def wire_body(self) -> dict[str, JsonValue]:
        """Serialize only documented native v1 names."""
        return {
            "messages": [
                {"role": message.role, "content": message.content}
                for message in self.messages
            ],
            "maxTokens": self.max_tokens,
            "repeatPenalty": self.repeat_penalty,
            "stopBefore": list(self.stop_before),
        }


class NativeV1Result(BaseModel):
    """Native v1 result with length-based usage fields."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    message: ChatMessage
    stop_reason: str = Field(
        validation_alias=AliasChoices("stopReason", "finishReason")
    )
    input_length: int = Field(validation_alias="inputLength")
    output_length: int = Field(validation_alias="outputLength")


class NativeV1Response(BaseModel):
    """Validated native v1 response envelope."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    result: NativeV1Result


class NativeV1Client:
    """Wire-injectable native v1 client."""

    _executor: HttpExecutor

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        budget: RequestBudget,
        transport: httpx2.AsyncBaseTransport | None = None,
    ) -> None:
        """Bind the native v1 endpoint to bounded execution."""
        self._executor = HttpExecutor(
            client=create_async_client(
                base_url=base_url, api_key=api_key, transport=transport
            ),
            budget=budget,
        )

    async def chat(self, request: NativeV1ChatRequest) -> NativeV1Response:
        """Generate through `/v1/chat-completions/{model}`."""
        response = await self._executor.request(
            method="POST",
            path=f"v1/chat-completions/{request.model}",
            estimated_tokens=request.max_tokens,
            json_body=request.wire_body(),
        )
        return NativeV1Response.model_validate_json(response.content)

    async def chat_stream(self, request: NativeV1ChatRequest) -> ParsedStream:
        """Parse a native v1 SSE chat stream."""
        response = await self._executor.request(
            method="POST",
            path=f"v1/chat-completions/{request.model}",
            estimated_tokens=request.max_tokens,
            json_body=request.wire_body(),
            headers={"Accept": "text/event-stream"},
        )
        return parse_sse(response.content)
