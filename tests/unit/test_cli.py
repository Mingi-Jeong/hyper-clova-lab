import socket
from pathlib import Path
from typing import Final, NoReturn

import pytest
from typer.testing import CliRunner

from hcx_eval.cli import app

NETWORK_ATTEMPT_MESSAGE: Final = "Unexpected network attempt."


def test_default_cli_reports_offline_mode_without_opening_a_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def network_forbidden() -> NoReturn:
        raise AssertionError(NETWORK_ATTEMPT_MESSAGE)

    monkeypatch.setattr(socket, "create_connection", network_forbidden)

    result = CliRunner().invoke(app)

    assert result.exit_code == 0
    assert result.stdout == "Offline scaffold ready; no network action was performed.\n"


def test_build_cases_cli_writes_bounded_structured_artifact(tmp_path: Path) -> None:
    # Given: an output path outside the protected input tree.
    output = tmp_path / "structured.jsonl"

    # When: the offline case builder is invoked explicitly.
    result = CliRunner().invoke(
        app,
        [
            "build-cases",
            "--dataset",
            "structured",
            "--data-root",
            "processed-data",
            "--output",
            str(output),
        ],
    )

    # Then: it reports only the deterministic inventory and writes no source file.
    assert result.exit_code == 0
    assert "352 cases" in result.stdout
    assert output.read_bytes().count(b"\n") == 352
