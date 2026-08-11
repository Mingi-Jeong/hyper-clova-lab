import socket
from pathlib import Path
from typing import Final, NoReturn

import pytest
from typer.testing import CliRunner

from hcx_eval.cli import app
from hcx_eval.schemas.model import Capability, ModelRecord, ModelStatus

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


def test_smoke_cli_defaults_to_dry_run_and_never_opens_a_socket(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a local live-model registry and a transport tripwire.
    registry = tmp_path / "registry.json"
    model = ModelRecord(
        identifier="HCX-005",
        status=ModelStatus.LIVE,
        api_families=("openai-compatible",),
        capabilities=(Capability(name="generation", supported=True),),
        evidence=("fixture",),
    )
    _ = registry.write_text(
        f"[{model.model_dump_json()}]",
        encoding="utf-8",
    )

    def network_forbidden() -> NoReturn:
        raise AssertionError(NETWORK_ATTEMPT_MESSAGE)

    monkeypatch.setattr(socket, "create_connection", network_forbidden)

    # When: no execution flag is supplied.
    result = CliRunner().invoke(
        app,
        [
            "smoke",
            "--registry",
            str(registry),
            "--data-root",
            "processed-data",
            "--run-id",
            "smoke-preflight",
            "--max-requests",
            "1",
        ],
    )

    # Then: the complete plan is printed and no request is dispatched.
    assert result.exit_code == 0
    assert "dry-run" in result.stdout
    assert "requests=1" in result.stdout
    assert "external_requests=0" in result.stdout
