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
from hcx_eval.discovery.docs_registry import parse_docs_snapshot
from hcx_eval.registry.discovery import discover_models, write_model_registry
from hcx_eval.reports.models import ReportBundle
from hcx_eval.reports.writer import generate_reports
from hcx_eval.runners.generation import (
    AdapterGenerationBackend,
    GenerationPlan,
    execute_generation_plan,
    plan_generation,
)
from hcx_eval.runners.preflight import SpecializedPhase, plan_specialized_phases
from hcx_eval.runners.red_team import load_red_team_cases
from hcx_eval.runners.smoke import plan_smoke
from hcx_eval.schemas.case import EvaluationCase
from hcx_eval.schemas.model import ModelRecord

OFFLINE_STATUS: Final = "Offline scaffold ready; no network action was performed."
_DEFAULT_DATA_ROOT: Final = Path("processed-data")
_DEFAULT_DOCS_ROOT: Final = Path("naver-clova-studio-instructions-all-docs")
_DEFAULT_MODEL_EVALUATION_ROOT: Final = Path("docs/model-evaluation")
_DEFAULT_RESULTS_ROOT: Final = Path("results")
_DEFAULT_CASE_OUTPUT: Final = Path("cases/generated/structured.jsonl")
_DEFAULT_REGISTRY: Final = Path("results/model-registry.json")
_DEFAULT_CONFIG: Final = Path("configs/benchmark.default.yaml")
_DEFAULT_RUN_ID: Final = "dry-run"
_DEFAULT_DOCS_SNAPSHOT: Final = Path(
    "naver-clova-studio-instructions-all-docs/naver_clova_studio_all_docs.json"
)
_DEFAULT_MODEL_CATALOG: Final = Path(
    "docs/model-evaluation/02_HYPERCLOVA_MODEL_CATALOG.md"
)
_DEFAULT_DISCOVERY_RAW: Final = Path("results/discovery/models.raw.json")
_DEFAULT_SAFETY_CASES: Final = Path("cases/reviewed/financial_safety.jsonl")
_MODEL_RECORDS: Final = TypeAdapter(tuple[ModelRecord, ...])
_EVALUATION_CASE: Final = TypeAdapter(EvaluationCase)
_REPORT_BUNDLE: Final = TypeAdapter(ReportBundle)
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


@app.command("inventory")
def inventory_command(
    data_root: Annotated[Path, typer.Option()] = _DEFAULT_DATA_ROOT,
    docs_root: Annotated[Path, typer.Option()] = _DEFAULT_DOCS_ROOT,
    model_evaluation_root: Annotated[
        Path, typer.Option()
    ] = _DEFAULT_MODEL_EVALUATION_ROOT,
) -> None:
    """Hash protected sources read-only without making a network request."""
    for label, root in (
        ("processed-data", data_root),
        ("naver-docs", docs_root),
        ("model-evaluation", model_evaluation_root),
    ):
        inventory = build_inventory(root)
        prefix = f"{label} files={inventory.file_count} bytes={inventory.total_bytes}"
        typer.echo(f"{prefix} sha256={inventory.sha256}")


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


def _load_report_bundle(path: Path, run_id: str) -> ReportBundle:
    try:
        bundle = _REPORT_BUNDLE.validate_json(path.read_bytes())
    except (OSError, ValueError) as error:
        message = f"cannot load normalized report bundle {path}: {error}"
        raise typer.BadParameter(message) from error
    if bundle.run_id != run_id:
        message = "report bundle run ID does not match --run-id"
        raise typer.BadParameter(message)
    return bundle


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


@app.command("discover")
def discover_command(  # noqa: PLR0913,PLR0917 - explicit network safety controls.
    docs_snapshot: Annotated[Path, typer.Option()] = _DEFAULT_DOCS_SNAPSHOT,
    catalog: Annotated[Path, typer.Option()] = _DEFAULT_MODEL_CATALOG,
    registry: Annotated[Path, typer.Option()] = _DEFAULT_REGISTRY,
    raw_output: Annotated[Path, typer.Option()] = _DEFAULT_DISCOVERY_RAW,
    config: Annotated[Path, typer.Option()] = _DEFAULT_CONFIG,
    max_requests: Annotated[int, typer.Option(min=1, max=1)] = 1,
    dry_run: Annotated[bool, typer.Option("--dry-run/--execute")] = True,
) -> None:
    """Plan or execute exactly one OpenAI-compatible model-list request."""
    documented = parse_docs_snapshot(docs_snapshot, catalog_path=catalog).models
    if dry_run:
        prefix = f"dry-run documented_models={len(documented)} planned_requests=1"
        typer.echo(f"{prefix} ceiling={max_requests} external_requests=0")
        return
    settings = load_settings(config)
    if not settings.execute:
        message = "execution is disabled; keep dry-run or set EXECUTE=true"
        raise typer.BadParameter(message)
    if settings.max_requests_per_run < 1:
        message = "configured request ceiling does not permit discovery"
        raise typer.BadParameter(message)
    if registry.exists() or raw_output.exists():
        message = "discovery outputs already exist; choose new write-once paths"
        raise typer.BadParameter(message)
    key = settings.clova_studio_api_key
    if key is None:
        message = "execution requires an API key"
        raise typer.BadParameter(message)
    budget = RequestBudget(
        RequestPolicy(
            execute=True,
            max_requests=max_requests,
            max_tokens=settings.max_tokens_per_run,
        )
    )
    client = OpenAICompatibleClient(
        base_url=settings.clova_openai_base_url,
        api_key=key.get_secret_value(),
        budget=budget,
    )
    invoke = partial(
        discover_models,
        client=client,
        documented=documented,
        raw_output=raw_output,
    )
    result = anyio.run(invoke)
    _ = write_model_registry(result.models, registry)
    prefix = f"discovered_models={len(result.models)}"
    typer.echo(f"{prefix} external_requests={result.external_requests}")


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
    latency_warmups: Annotated[int, typer.Option(min=0)] = 1,
    latency_samples: Annotated[int, typer.Option(min=1)] = 2,
    safety_cases: Annotated[Path, typer.Option()] = _DEFAULT_SAFETY_CASES,
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
    specialized_names = {phase.value for phase in SpecializedPhase}
    if any(phase in specialized_names for phase in selected_phases):
        registry_records = _load_registry(registry)
        preflight = plan_specialized_phases(
            _load_cases(cases),
            registry_records,
            phases=selected_phases,
            model_selectors=selected_models,
            max_requests=max_requests,
            latency_warmups=latency_warmups,
            latency_samples=latency_samples,
            safety_case_count=len(load_red_team_cases(safety_cases)),
        )
        if not dry_run:
            message = (
                "specialized phase execution is outside approved Task 16; use dry-run"
            )
            raise typer.BadParameter(message)
        phase_names = ",".join(phase.value for phase in preflight.phases)
        model_names = ",".join(preflight.models) or "none"
        prefix = f"dry-run run={run_id} phases={phase_names}"
        summary = f"{prefix} requests={preflight.request_count}"
        summary += f" ceiling={preflight.max_requests} models={model_names}"
        typer.echo(f"{summary} external_requests=0")
        return
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


@app.command("report")
def report_command(
    run_id: Annotated[str, typer.Option()],
    bundle: Annotated[Path | None, typer.Option()] = None,
    results_root: Annotated[Path, typer.Option()] = _DEFAULT_RESULTS_ROOT,
) -> None:
    """Generate separate write-once reports from normalized local artifacts."""
    bundle_path = (
        results_root / run_id / "normalized" / "report-bundle.json"
        if bundle is None
        else bundle
    )
    try:
        paths = generate_reports(
            _load_report_bundle(bundle_path, run_id),
            results_root=results_root,
        )
    except (FileExistsError, ValueError) as error:
        raise typer.BadParameter(str(error)) from error
    typer.echo(f"actual_results={paths.actual_results}")
    typer.echo(f"pension_insights={paths.pension_insights}")
