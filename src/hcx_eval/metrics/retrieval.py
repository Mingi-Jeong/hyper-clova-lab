"""Binary-relevance retrieval metrics."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def _validate(relevant: Sequence[str], k: int) -> set[str]:
    if k <= 0:
        message = "k must be positive"
        raise ValueError(message)
    relevant_set = set(relevant)
    if not relevant_set:
        message = "relevant IDs must not be empty"
        raise ValueError(message)
    return relevant_set


def recall_at_k(retrieved: Sequence[str], relevant: Sequence[str], *, k: int) -> float:
    """Return the fraction of unique relevant IDs retrieved in the first k ranks."""
    relevant_set = _validate(relevant, k)
    return len(set(retrieved[:k]).intersection(relevant_set)) / len(relevant_set)


def reciprocal_rank(
    retrieved: Sequence[str],
    relevant: Sequence[str],
    *,
    k: int,
) -> float:
    """Return reciprocal rank of the first relevant result, or zero."""
    relevant_set = _validate(relevant, k)
    for rank, identifier in enumerate(retrieved[:k], start=1):
        if identifier in relevant_set:
            return 1 / rank
    return 0.0


def ndcg_at_k(retrieved: Sequence[str], relevant: Sequence[str], *, k: int) -> float:
    """Compute binary nDCG while ignoring repeated identifiers after first rank."""
    relevant_set = _validate(relevant, k)
    seen: set[str] = set()
    dcg = 0.0
    for rank, identifier in enumerate(retrieved[:k], start=1):
        if identifier in relevant_set and identifier not in seen:
            dcg += 1 / math.log2(rank + 1)
        seen.add(identifier)
    ideal_hits = min(len(relevant_set), k)
    ideal = sum(1 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / ideal
