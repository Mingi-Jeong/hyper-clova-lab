import pytest

from hcx_eval.runners.preflight import plan_specialized_phases
from hcx_eval.schemas.case import EvaluationCase
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus


def _case(case_id: str) -> EvaluationCase:
    return EvaluationCase.model_validate(
        {
            "case_id": case_id,
            "task": "faq",
            "prompt": f"question {case_id}",
            "expected": {"answer": f"answer {case_id}"},
            "source_ids": [f"source:{case_id}"],
            "dataset_sha256": "a" * 64,
            "metadata": {"review_status": "reviewed"},
        }
    )


def test_specialized_preflight_accounts_for_every_phase_expansion() -> None:
    model = ModelRecord(
        identifier="HCX-MOCK",
        status=ModelStatus.LIVE,
        api_families=("openai-compatible", "api-tool"),
        capabilities=(
            Capability(name="generation", supported=True),
            Capability(name="embedding", supported=True),
        ),
        evidence=("fixture",),
    )

    plan = plan_specialized_phases(
        (_case("A"), _case("B")),
        (model,),
        phases=("latency", "embeddings", "api-tools", "safety"),
        model_selectors=("all",),
        max_requests=15,
        latency_warmups=1,
        latency_samples=2,
        safety_case_count=7,
    )

    assert plan.request_count == 15  # latency 3 + embedding 4 + tool 1 + safety 7
    assert plan.models == ("HCX-MOCK",)


def test_specialized_preflight_refuses_over_ceiling_and_mixed_tasks() -> None:
    with pytest.raises(ValueError, match="15 requests exceeds ceiling 14"):
        _ = plan_specialized_phases(
            (_case("A"), _case("B")),
            (
                ModelRecord(
                    identifier="HCX-MOCK",
                    status=ModelStatus.LIVE,
                    api_families=("api-tool",),
                    capabilities=(
                        Capability(name="generation", supported=True),
                        Capability(name="embedding", supported=True),
                    ),
                    evidence=("fixture",),
                ),
            ),
            phases=("latency", "embeddings", "api-tools", "safety"),
            model_selectors=("all",),
            max_requests=14,
            latency_warmups=1,
            latency_samples=2,
            safety_case_count=7,
        )

    with pytest.raises(ValueError, match="cannot be mixed"):
        _ = plan_specialized_phases(
            (_case("A"),),
            (),
            phases=("latency", "faq"),
            model_selectors=("all",),
            max_requests=10,
            latency_warmups=1,
            latency_samples=2,
            safety_case_count=7,
        )
