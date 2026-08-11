"""Set-based citation precision, recall, and F1."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class CitationScore(BaseModel):
    """Deterministic citation score triple."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")

    precision: float = Field(ge=0, le=1)
    recall: float = Field(ge=0, le=1)
    f1: float = Field(ge=0, le=1)


def citation_score(cited: tuple[str, ...], gold: tuple[str, ...]) -> CitationScore:
    """Score unique citation IDs with explicit empty-set semantics."""
    cited_set = set(cited)
    gold_set = set(gold)
    correct = len(cited_set.intersection(gold_set))
    precision = (
        1.0
        if not cited_set and not gold_set
        else (0.0 if not cited_set else correct / len(cited_set))
    )
    recall = 1.0 if not gold_set else correct / len(gold_set)
    f1 = (
        0.0
        if precision + recall == 0
        else (2 * precision * recall) / (precision + recall)
    )
    return CitationScore(precision=precision, recall=recall, f1=f1)
