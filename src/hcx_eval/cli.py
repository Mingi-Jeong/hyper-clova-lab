"""Offline-safe command-line interface for the evaluation harness."""

from typing import Final

import typer

OFFLINE_STATUS: Final = "Offline scaffold ready; no network action was performed."

app: typer.Typer = typer.Typer(
    add_completion=False,
    help="HyperCLOVA X financial evaluation harness.",
    invoke_without_command=True,
    no_args_is_help=False,
)


@app.callback()
def main() -> None:
    typer.echo(OFFLINE_STATUS)
