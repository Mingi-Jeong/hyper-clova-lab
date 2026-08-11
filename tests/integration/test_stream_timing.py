from __future__ import annotations

import httpx2
import pytest

from hcx_eval.clients.base import RequestBudget, RequestPolicy
from hcx_eval.clients.openai_compat import (
    OpenAIChatRequest,
    OpenAICompatibleClient,
)
from hcx_eval.clients.sse import ParsedStream, SseEvent
from hcx_eval.clients.types import ChatMessage
from hcx_eval.runners.latency import derive_stream_timing


def test_stream_timing_uses_non_empty_tokens_and_monotonic_events() -> None:
    stream = ParsedStream(
        events=(
            SseEvent(event="metadata", received_at=10.10, data={}, content=""),
            SseEvent(event="token", received_at=10.20, data={}, content="안"),
            SseEvent(event="token", received_at=10.25, data={}, content="녕"),
        ),
        first_content_at=10.20,
        response_headers_at=10.05,
        closed_at=10.30,
    )

    timing = derive_stream_timing(stream, dispatched_at=10.0, output_tokens=2)

    assert timing.response_headers_ms == pytest.approx(50)
    assert timing.ttft_ms == pytest.approx(200)
    assert timing.final_content_ms == pytest.approx(250)
    assert timing.close_ms == pytest.approx(300)
    assert timing.e2e_ms == pytest.approx(300)
    assert timing.tpot_ms == pytest.approx(50)
    assert timing.inter_token_gap_p95_ms == pytest.approx(50)
    assert timing.max_stall_ms == pytest.approx(50)


@pytest.mark.anyio
async def test_real_stream_adapter_captures_headers_events_and_close() -> None:
    raw = (
        b'data: {"choices":[{"delta":{"content":""}}]}\n\n'
        b'data: {"choices":[{"delta":{"content":"ok"}}]}\n\n'
        b"data: [DONE]\n\n"
    )

    async def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, content=raw, request=request)

    client = OpenAICompatibleClient(
        base_url="https://offline.invalid/v1/openai",
        api_key="synthetic-key",
        budget=RequestBudget(RequestPolicy(execute=True, max_requests=1, max_tokens=8)),
        transport=httpx2.MockTransport(handler),
    )

    stream = await client.chat_stream(
        OpenAIChatRequest(
            model="HCX-005",
            messages=(ChatMessage(role="user", content="hi"),),
            max_tokens=8,
        )
    )

    assert stream.response_headers_at is not None
    assert stream.first_content_at is not None
    assert stream.closed_at is not None
    assert stream.response_headers_at <= stream.events[0].received_at
    assert stream.events[-1].received_at <= stream.closed_at
