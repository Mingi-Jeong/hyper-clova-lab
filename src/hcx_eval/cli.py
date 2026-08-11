"""Offline-safe command-line interface for the evaluation harness."""

from enum import StrEnum
from functools import partial
from pathlib import Path
from typing import Annotated, Final

import anyio
import typer
from pydantic import TypeAdapter

from hcx_eval.clients.base import RequestBudget, RequestPolicy
from hcx_eval.clients.native_v1 import NativeV1Client
from hcx_eval.clients.native_v3 import NativeV3Client
from hcx_eval.clients.openai_compat import OpenAICompatibleClient
from hcx_eval.config import HarnessSettings, load_settings
from hcx_eval.datasets.cases import build_structured_cases, write_case_bundle
from hcx_eval.datasets.inventory import build_inventory
from hcx_eval.runners.generation import (
    AdapterGenerationBackend,
    GenerationPlan,
    execute_generation_plan,
    plan_generation,
)
from hcx_eval.runners.smoke import plan_smoke
from hcx_eval.schemas.case import EvaluationCase
from hcx_eval.schemas.model import ModelRecord

OFFLINE_STATUS: Final = "Offline scaffold ready; no network action was performed."
_DEFAULT_DATA_ROOT: Final = Path("processed-data")
_DEFAULT_CASE_OUTPUT: Final = Path("cases/generated/structured.jsonl")
_DEFAULT_REGISTRY: Final = Path("results/model-registry.json")
_DEFAULT_CONFIG: Final = Path("configs/benchmark.default.yaml")
_DEFAULT_RUN_ID: Final = "dry-run"
_MODEL_RECORDS: Final = TypeAdapter(tuple[ModelRecord, ...])
_EVALUATION_CASE: Final = TypeAdapter(EvaluationCase)
_PHASE_ALIASES: Final = {
    "faq": "default_option_qa",
    "transfer-code": "transfer_code_to_reason",
    "transfer-reason": "transfer_reason_to_code",
}

app: typer.Typer = typer.Typer(
    add_completion=False,
    help="HyperCLOVA X financial evaluation harness.",
    invoke_without_command=True,
    no_args_is_help=False,
)


@app.callback()
def main(context: typer.Context) -> None:
    """Keep no-command invocation offline and quiet before subcommands."""
    if context.invoked_subcommand is None:
        typer.echo(OFFLINE_STATUS)


class DatasetSelection(StrEnum):
    """Bounded set of source-backed case bundles."""

    STRUCTURED = "structured"


@app.command("build-cases")
def build_cases_command(
    dataset: Annotated[DatasetSelection, typer.Option()] = DatasetSelection.STRUCTURED,
    data_root: Annotated[Path, typer.Option()] = _DEFAULT_DATA_ROOT,
    output: Annotated[Path, typer.Option()] = _DEFAULT_CASE_OUTPUT,
) -> None:
    """Build deterministic cases without making a network request."""
    _ = dataset
    summary = write_case_bundle(build_structured_cases(data_root), output)
    prefix = f"Built {summary.case_count} cases at {summary.output}"
    typer.echo(f"{prefix} (sha256={summary.sha256}).")


def _load_registry(path: Path) -> tuple[ModelRecord, ...]:
    try:
        return _MODEL_RECORDS.validate_json(path.read_bytes())
    except (OSError, ValueError) as error:
        message = f"cannot load model registry {path}: {error}"
        raise typer.BadParameter(message) from error


def _load_cases(path: Path) -> tuple[EvaluationCase, ...]:
    try:
        return tuple(
            _EVALUATION_CASE.validate_json(line)
            for line in path.read_bytes().splitlines()
            if line
        )
    except (OSError, ValueError) as error:
        message = f"cannot load evaluation cases {path}: {error}"
        raise typer.BadParameter(message) from error


def _backend(settings: HarnessSettings) -> AdapterGenerationBackend:
    key = settings.clova_studio_api_key
    if key is None:
        message = "execution requires an API key"
        raise typer.BadParameter(message)
    budget = RequestBudget(
        RequestPolicy(
            execute=settings.execute,
            max_requests=settings.max_requests_per_run,
            max_tokens=settings.max_tokens_per_run,
        )
    )
    secret = key.get_secret_value()
    return AdapterGenerationBackend(
        openai=OpenAICompatibleClient(
            base_url=settings.clova_openai_base_url,
            api_key=secret,
            budget=budget,
        ),
        native_v1=NativeV1Client(
            base_url=settings.clova_studio_base_url,
            api_key=secret,
            budget=budget,
        ),
        native_v3=NativeV3Client(
            base_url=settings.clova_studio_base_url,
            api_key=secret,
            budget=budget,
        ),
    )


def _execute(plan: GenerationPlan, config: Path) -> None:
    settings = load_settings(config)
    if not settings.execute:
        message = "execution is disabled; keep dry-run or set EXECUTE=true"
        raise typer.BadParameter(message)
    if plan.request_count > settings.max_requests_per_run:
        message = "plan exceeds configured request ceiling"
        raise typer.BadParameter(message)
    docs_sha256 = build_inventory(settings.naver_docs_root).sha256
    invoke = partial(
        execute_generation_plan,
        plan,
        backend=_backend(settings),
        results_root=settings.results_root,
        docs_snapshot_sha256=docs_sha256,
    )
    summary = anyio.run(invoke)
    prefix = f"run={summary.run_id} executed={summary.executed}"
    typer.echo(f"{prefix} skipped={summary.skipped} failed={summary.failed}")


def _dry_run_message(plan: GenerationPlan) -> str:
    models = ",".join(sorted({job.model for job in plan.jobs})) or "none"
    prefix = f"dry-run run={plan.run_id} requests={plan.request_count}"
    return f"{prefix} ceiling={plan.max_requests} models={models} external_requests=0"


@app.command("smoke")
def smoke_command(  # noqa: PLR0913,PLR0917 - explicit CLI safety controls.
    registry: Annotated[Path, typer.Option()] = _DEFAULT_REGISTRY,
    data_root: Annotated[Path, typer.Option()] = _DEFAULT_DATA_ROOT,
    config: Annotated[Path, typer.Option()] = _DEFAULT_CONFIG,
    run_id: Annotated[str, typer.Option()] = "smoke-dry-run",
    max_requests: Annotated[int, typer.Option(min=1)] = 20,
    max_tokens: Annotated[int, typer.Option(min=1)] = 8,
    dry_run: Annotated[bool, typer.Option("--dry-run/--execute")] = True,
) -> None:
    """Plan or execute a bounded one-request-per-live-model smoke run."""
    dataset_sha256 = build_inventory(data_root / "datasets").sha256
    plan = plan_smoke(
        _load_registry(registry),
        run_id=run_id,
        dataset_sha256=dataset_sha256,
        max_requests=max_requests,
        max_tokens=max_tokens,
    )
    if dry_run:
        typer.echo(_dry_run_message(plan))
        return
    _execute(plan, config)


@app.command("run")
def run_command(  # noqa: PLR0913,PLR0917 - explicit CLI safety controls.
    registry: Annotated[Path, typer.Option()] = _DEFAULT_REGISTRY,
    cases: Annotated[Path, typer.Option()] = _DEFAULT_CASE_OUTPUT,
    config: Annotated[Path, typer.Option()] = _DEFAULT_CONFIG,
    run_id: Annotated[str, typer.Option()] = _DEFAULT_RUN_ID,
    phases: Annotated[str, typer.Option("--phases", "--phase")] = "faq",
    models: Annotated[str, typer.Option()] = "all",
    max_requests: Annotated[int, typer.Option(min=1)] = 100,
    max_tokens: Annotated[int, typer.Option(min=1)] = 256,
    dry_run: Annotated[bool, typer.Option("--dry-run/--execute")] = True,
) -> None:
    """Plan or execute selected generation phases without implicit expansion."""
    selected_phases = tuple(
        _PHASE_ALIASES.get(value.strip(), value.strip())
        for value in phases.split(",")
        if value.strip()
    )
    selected_models = tuple(
        value.strip() for value in models.split(",") if value.strip()
    )
    plan = plan_generation(
        _load_cases(cases),
        _load_registry(registry),
        run_id=run_id,
        max_requests=max_requests,
        max_tokens=max_tokens,
        phases=selected_phases,
        model_selectors=selected_models,
    )
    if dry_run:
        typer.echo(_dry_run_message(plan))
        return
    _execute(plan, config)
