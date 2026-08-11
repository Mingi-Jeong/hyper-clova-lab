from math import log2

import pytest

from hcx_eval.metrics.citations import citation_score
from hcx_eval.metrics.retrieval import ndcg_at_k, recall_at_k, reciprocal_rank


def test_retrieval_metrics_follow_binary_relevance_definitions() -> None:
    retrieved = ("d2", "d1", "d4", "d3")
    relevant = ("d1", "d3")

    assert recall_at_k(retrieved, relevant, k=3) == 0.5
    assert reciprocal_rank(retrieved, relevant, k=4) == 0.5
    expected = (1 / log2(3) + 1 / log2(5)) / (1 + 1 / log2(3))
    assert ndcg_at_k(retrieved, relevant, k=4) == pytest.approx(expected)


def test_citation_score_deduplicates_ids_and_handles_empty_sets() -> None:
    score = citation_score(("S1", "S2", "S2"), ("S2", "S3"))
    assert score.precision == 0.5
    assert score.recall == 0.5
    assert score.f1 == 0.5

    empty = citation_score((), ())
    assert empty.precision == 1.0
    assert empty.recall == 1.0
    assert empty.f1 == 1.0
