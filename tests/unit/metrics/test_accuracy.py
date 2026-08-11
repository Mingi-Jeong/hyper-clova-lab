import pytest

from hcx_eval.metrics.accuracy import (
    contradiction_flags,
    exact_match,
    macro_f1,
    required_fact_recall,
)


def test_exact_match_and_required_fact_recall_normalize_korean_spacing() -> None:
    assert exact_match("  HCX-005\n", "hcx-005") == 1.0
    assert exact_match("01", "1") == 0.0
    assert required_fact_recall(
        "옵트인이 가능하며 실제 보유 없음 상태입니다.",
        ("옵트인", "실제보유없음", "전량매도"),
    ) == pytest.approx(2 / 3)


def test_macro_f1_and_contradiction_flags_are_deterministic() -> None:
    assert macro_f1(("a", "a", "b", "c"), ("a", "b", "b", "c")) == pytest.approx(7 / 9)
    assert contradiction_flags(
        "원금 보장이라고 단정하면 안 됩니다.",
        ("원금보장", "수익률 확정"),
    ) == ("원금보장",)


def test_accuracy_metrics_reject_invalid_empty_inputs() -> None:
    with pytest.raises(ValueError, match="same non-zero length"):
        _ = macro_f1((), ())
    with pytest.raises(ValueError, match="required facts"):
        _ = required_fact_recall("answer", ())
