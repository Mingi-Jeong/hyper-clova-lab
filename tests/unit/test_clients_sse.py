import pytest

from hcx_eval.clients.sse import MalformedSseError, parse_sse


def test_sse_parser_ignores_empty_metadata_for_first_content() -> None:
    # Given
    raw = (
        b'event: token\ndata: {"message":{"role":"assistant","content":""}}\n\n'
        b'event: token\ndata: {"message":{"role":"assistant","content":"hi"}}\n\n'
    )
    times = iter((1.0, 2.0))

    # When
    stream = parse_sse(raw, clock=lambda: next(times))

    # Then
    assert len(stream.events) == 2
    assert stream.first_content_at == 2.0
    assert stream.events[1].content == "hi"


def test_sse_parser_rejects_malformed_json() -> None:
    # Given
    raw = b"event: token\ndata: {bad}\n\n"

    # When / Then
    with pytest.raises(MalformedSseError):
        _ = parse_sse(raw)
