from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import JsonValue, TypeAdapter

from hcx_eval.clients.base import ErrorKind, ProviderApiError
from hcx_eval.runners.generation import (
    GenerationOutcome,
    execute_generation_plan,
    plan_generation,
)
from hcx_eval.schemas.case import EvaluationCase
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus
from hcx_eval.schemas.results import Usage

if TYPE_CHECKING:
    from pathlib import Path

    from hcx_eval.runners.generation import GenerationJob

_JSON_OBJECT = TypeAdapter(dict[str, JsonValue])
_STRING = TypeAdapter(str)


def _case(case_id: str) -> EvaluationCase:
    return EvaluationCase.model_validate(
        {
            "case_id": case_id,
            "task": "default_option_qa",
            "prompt": f"question {case_id}",
            "expected": {"answer": "gold"},
            "source_ids": ["S1"],
            "dataset_sha256": "a" * 64,
            "metadata": {"split": "test", "review_status": "source_verified"},
        }
    )


def _live_model() -> ModelRecord:
    return ModelRecord(
        identifier="HCX-005",
        status=ModelStatus.LIVE,
        api_families=("openai-compatible",),
        capabilities=(Capability(name="generation", supported=True),),
        evidence=("fixture",),
    )


class MixedBackend:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def generate(self, job: GenerationJob) -> GenerationOutcome:
        self.calls.append(job.case.case_id)
        if job.case.case_id == "FAQ-0002-R":
            raise ProviderApiError(
                kind=ErrorKind.SERVER,
                endpoint="https://offline.invalid/chat/completions",
                http_status=500,
                provider_code="50000",
                response_body=b'{"error":"safe failure"}',
            )
        return GenerationOutcome(
            text="answer",
            raw={"answer": "answer"},
            usage=Usage(
                prompt_tokens=2,
                completion_tokens=1,
                total_tokens=3,
            ),
            http_status=200,
            provider_status_code="20000",
        )


@pytest.mark.anyio
async def test_generation_runner_records_failures_and_resumes_without_overwrite(
    tmp_path: Path,
) -> None:
    cases = (_case("FAQ-0001-R"), _case("FAQ-0002-R"))
    plan = plan_generation(
        cases,
        (_live_model(),),
        run_id="run-1",
        max_requests=2,
        max_tokens=8,
        phases=("default_option_qa",),
        model_selectors=("all",),
    )
    backend = MixedBackend()

    first = await execute_generation_plan(
        plan,
        backend=backend,
        results_root=tmp_path,
        docs_snapshot_sha256="b" * 64,
    )
    second = await execute_generation_plan(
        plan,
        backend=backend,
        results_root=tmp_path,
        docs_snapshot_sha256="b" * 64,
    )

    assert first.planned == 2
    assert first.executed == 2
    assert first.failed == 1
    assert first.skipped == 0
    assert second.executed == 0
    assert second.skipped == 2
    assert backend.calls == ["FAQ-0001-R", "FAQ-0002-R"]

    raw_files = tuple(sorted((tmp_path / "run-1" / "raw").glob("*.jsonl")))
    records = tuple(
        _JSON_OBJECT.validate_json(line)
        for path in raw_files
        for line in path.read_bytes().splitlines()
    )
    assert len(records) == 2
    assert sum(record["error"] is not None for record in records) == 1
    assert {_STRING.validate_python(record["case_id"]) for record in records} == {
        "FAQ-0001-R",
        "FAQ-0002-R",
    }


def test_generation_plan_filters_models_and_phases_before_ceiling() -> None:
    cases = (_case("FAQ-0001-R"), _case("FAQ-0002-R"))
    model = _live_model()

    plan = plan_generation(
        cases,
        (model,),
        run_id="run-1",
        max_requests=1,
        max_tokens=8,
        phases=("not-selected",),
        model_selectors=("all",),
    )
    assert plan.request_count == 0

    with pytest.raises(ValueError, match="unknown model selectors"):
        _ = plan_generation(
            cases,
            (model,),
            run_id="run-1",
            max_requests=2,
            max_tokens=8,
            phases=("default_option_qa",),
            model_selectors=("HCX-MISSING",),
        )
