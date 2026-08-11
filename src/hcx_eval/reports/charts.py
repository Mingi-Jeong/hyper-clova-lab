# ruff: noqa: E501
"""Quality-latency-cost Pareto analysis and deterministic SVG charts."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

from hcx_eval.security import redact_text

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from hcx_eval.reports.models import ParetoPoint

_WIDTH = 720
_HEIGHT = 450
_MARGIN = 60


def pareto_frontier(points: Sequence[ParetoPoint]) -> tuple[ParetoPoint, ...]:
    """Retain points not dominated on quality, latency, and request cost."""
    return tuple(
        point
        for point in points
        if not any(
            other.label != point.label
            and other.quality >= point.quality
            and other.latency_ms <= point.latency_ms
            and other.cost_per_request <= point.cost_per_request
            and (
                other.quality > point.quality
                or other.latency_ms < point.latency_ms
                or other.cost_per_request < point.cost_per_request
            )
            for other in points
        )
    )


def _x_coordinate(value: float, minimum: float, maximum: float) -> float:
    span = maximum - minimum
    ratio = 0.5 if span == 0 else (value - minimum) / span
    return _MARGIN + ratio * (_WIDTH - (2 * _MARGIN))


def _chart(
    points: Sequence[ParetoPoint],
    *,
    x_value: Callable[[ParetoPoint], float],
    x_label: str,
) -> bytes:
    values = tuple(x_value(point) for point in points)
    minimum, maximum = min(values), max(values)
    frontier = {point.label for point in pareto_frontier(points)}
    marks: list[str] = []
    for point in points:
        x = _x_coordinate(x_value(point), minimum, maximum)
        y = _HEIGHT - _MARGIN - (point.quality / 100) * (_HEIGHT - (2 * _MARGIN))
        label = escape(redact_text(point.label))
        if point.label in frontier:
            marks.append(
                f'<rect x="{x - 5:.2f}" y="{y - 5:.2f}" width="10" height="10" transform="rotate(45 {x:.2f} {y:.2f})" fill="#d95f02" />'
            )
        else:
            marks.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#1b9e77" />')
        marks.append(
            f'<text x="{x + 7:.2f}" y="{y - 7:.2f}" font-size="12">{label}</text>'
        )
    safe_x_label = escape(x_label)
    body = "\n  ".join(marks)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" height="{_HEIGHT}" viewBox="0 0 {_WIDTH} {_HEIGHT}">
  <rect width="100%" height="100%" fill="white" />
  <line x1="{_MARGIN}" y1="{_HEIGHT - _MARGIN}" x2="{_WIDTH - _MARGIN}" y2="{_HEIGHT - _MARGIN}" stroke="black" />
  <line x1="{_MARGIN}" y1="{_MARGIN}" x2="{_MARGIN}" y2="{_HEIGHT - _MARGIN}" stroke="black" />
  <text x="{_WIDTH / 2}" y="{_HEIGHT - 15}" text-anchor="middle" font-size="14">{safe_x_label}</text>
  <text x="18" y="{_HEIGHT / 2}" text-anchor="middle" font-size="14" transform="rotate(-90 18 {_HEIGHT / 2})">Quality score (higher is better)</text>
  <text x="{_WIDTH / 2}" y="28" text-anchor="middle" font-size="16">Measured Pareto candidates (diamond = 3-axis frontier)</text>
  {body}
</svg>
""".encode()


def render_pareto_charts(
    points: Sequence[ParetoPoint],
) -> dict[str, bytes]:
    """Render two projections, or no chart when measurements are absent."""
    if not points:
        return {}
    return {
        "quality-latency-pareto.svg": _chart(
            points,
            x_value=lambda point: point.latency_ms,
            x_label="Client E2E latency (ms, lower is better)",
        ),
        "quality-cost-pareto.svg": _chart(
            points,
            x_value=lambda point: point.cost_per_request,
            x_label="Cost per request (lower is better)",
        ),
    }
