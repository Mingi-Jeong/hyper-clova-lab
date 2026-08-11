"""Deterministic exact, classification, fact, and contradiction metrics."""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

_WHITESPACE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Normalize Unicode, case, and spacing without removing punctuation."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return _WHITESPACE.sub("", normalized)


def exact_match(actual: str, expected: str) -> float:
    """Return one only when normalized strings are identical."""
    return float(normalize_text(actual) == normalize_text(expected))


def macro_f1(expected: Sequence[str], actual: Sequence[str]) -> float:
    """Compute unweighted one-vs-rest F1 across the observed label union."""
    if not expected or len(expected) != len(actual):
        message = "expected and actual must have the same non-zero length"
        raise ValueError(message)
    labels = sorted(set(expected).union(actual))
    scores: list[float] = []
    for label in labels:
        true_positive = sum(
            gold == label and predicted == label
            for gold, predicted in zip(expected, actual, strict=True)
        )
        false_positive = sum(
            gold != label and predicted == label
            for gold, predicted in zip(expected, actual, strict=True)
        )
        false_negative = sum(
            gold == label and predicted != label
            for gold, predicted in zip(expected, actual, strict=True)
        )
        denominator = (2 * true_positive) + false_positive + false_negative
        scores.append(0.0 if denominator == 0 else (2 * true_positive) / denominator)
    return sum(scores) / len(scores)


def required_fact_recall(response: str, required_facts: Sequence[str]) -> float:
    """Measure normalized required-fact substring coverage."""
    if not required_facts or any(not normalize_text(fact) for fact in required_facts):
        message = "required facts must contain at least one non-empty value"
        raise ValueError(message)
    normalized_response = normalize_text(response)
    hits = sum(normalize_text(fact) in normalized_response for fact in required_facts)
    return hits / len(required_facts)


def contradiction_flags(
    response: str,
    forbidden_claims: Sequence[str],
) -> tuple[str, ...]:
    """Return forbidden claims found by explicit normalized substring matching."""
    normalized_response = normalize_text(response)
    return tuple(
        claim
        for claim in forbidden_claims
        if normalize_text(claim) and normalize_text(claim) in normalized_response
    )
