"""Offline-safe command-line interface for the evaluation harness."""

from enum import StrEnum
from pathlib import Path
from typing import Annotated, Final

import typer

from hcx_eval.datasets.cases import build_structured_cases, write_case_bundle

OFFLINE_STATUS: Final = "Offline scaffold ready; no network action was performed."
_DEFAULT_DATA_ROOT: Final = Path("processed-data")
_DEFAULT_CASE_OUTPUT: Final = Path("cases/generated/structured.jsonl")

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
