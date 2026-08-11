"""Strict Server-Sent Events parsing for CLOVA token streams."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict, JsonValue, TypeAdapter
from typing_extensions import override

_JSON: TypeAdapter[JsonValue] = TypeAdapter(JsonValue)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable


class _Message(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    content: str


class _NativeEvent(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    message: _Message


class _Delta(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    content: str


class _Choice(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    delta: _Delta


class _OpenAIEvent(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="allow")
    choices: tuple[_Choice, ...]


@dataclass(frozen=True, slots=True)
class MalformedSseError(ValueError):
    """An SSE event contained invalid JSON data."""

    event: str

    @override
    def __str__(self) -> str:
        return f"malformed JSON in SSE event {self.event or 'message'}"


@dataclass(frozen=True, slots=True)
class SseEvent:
    """One timestamped provider SSE event."""

    event: str
    received_at: float
    data: JsonValue
    content: str | None


@dataclass(frozen=True, slots=True)
class ParsedStream:
    """Parsed stream and first non-empty user-visible content time."""

    events: tuple[SseEvent, ...]
    first_content_at: float | None


def _content(value: JsonValue) -> str | None:
    try:
        native = _NativeEvent.model_validate(value)
    except ValueError:
        try:
            compatible = _OpenAIEvent.model_validate(value)
        except (ValueError, IndexError):
            return None
        else:
            return compatible.choices[0].delta.content
    else:
        return native.message.content


def parse_sse(
    raw: bytes, *, clock: Callable[[], float] = time.monotonic
) -> ParsedStream:
    """Parse SSE blocks and timestamp each received event."""
    events: list[SseEvent] = []
    first_content_at: float | None = None
    for block in raw.decode("utf-8").replace("\r\n", "\n").split("\n\n"):
        if not block.strip():
            continue
        event_name = "message"
        data_lines: list[str] = []
        for line in block.splitlines():
            if line.startswith("event:"):
                event_name = line[6:].strip()
            elif line.startswith("data:"):
                data_lines.append(line[5:].lstrip())
        data_text = "\n".join(data_lines)
        if data_text == "[DONE]":
            break
        try:
            data = _JSON.validate_json(data_text)
        except ValueError as error:
            raise MalformedSseError(event=event_name) from error
        received_at = clock()
        content = _content(data)
        if first_content_at is None and content:
            first_content_at = received_at
        events.append(
            SseEvent(
                event=event_name, received_at=received_at, data=data, content=content
            )
        )
    return ParsedStream(events=tuple(events), first_content_at=first_content_at)


async def parse_sse_lines(
    lines: AsyncIterator[str], *, clock: Callable[[], float] = time.monotonic
) -> ParsedStream:
    """Parse events as blank-line-delimited blocks arrive from the wire."""
    events: list[SseEvent] = []
    first_content_at: float | None = None
    block: list[str] = []
    async for line in lines:
        if line:
            block.append(line)
            continue
        parsed = parse_sse("\n".join(block).encode(), clock=clock)
        block.clear()
        events.extend(parsed.events)
        if first_content_at is None:
            first_content_at = parsed.first_content_at
    if block:
        parsed = parse_sse("\n".join(block).encode(), clock=clock)
        events.extend(parsed.events)
        if first_content_at is None:
            first_content_at = parsed.first_content_at
    return ParsedStream(events=tuple(events), first_content_at=first_content_at)
