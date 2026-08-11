import socket
from pathlib import Path
from typing import Final, NoReturn

import pytest
from typer.testing import CliRunner

from hcx_eval.cli import app
from hcx_eval.reports.models import (
    ArtifactReference,
    ReportBundle,
    ReportTableId,
    not_run_table,
)
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


def test_inventory_and_discovery_preflight_are_offline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def network_forbidden() -> NoReturn:
        raise AssertionError(NETWORK_ATTEMPT_MESSAGE)

    monkeypatch.setattr(socket, "create_connection", network_forbidden)

    inventory = CliRunner().invoke(app, ["inventory"])
    discovery = CliRunner().invoke(app, ["discover", "--dry-run"])

    assert inventory.exit_code == 0
    assert "processed-data files=208" in inventory.stdout
    assert "naver-docs files=2" in inventory.stdout
    assert "model-evaluation files=7" in inventory.stdout
    assert discovery.exit_code == 0
    assert "documented_models=11" in discovery.stdout
    assert "planned_requests=1" in discovery.stdout
    assert "external_requests=0" in discovery.stdout


def test_specialized_safety_phase_is_bounded_dry_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = tmp_path / "registry.json"
    model = ModelRecord(
        identifier="HCX-005",
        status=ModelStatus.LIVE,
        capabilities=(Capability(name="generation", supported=True),),
        evidence=("fixture",),
    )
    _ = registry.write_text(f"[{model.model_dump_json()}]", encoding="utf-8")

    def network_forbidden() -> NoReturn:
        raise AssertionError(NETWORK_ATTEMPT_MESSAGE)

    monkeypatch.setattr(socket, "create_connection", network_forbidden)
    result = CliRunner().invoke(
        app,
        [
            "run",
            "--phase",
            "safety",
            "--registry",
            str(registry),
            "--max-requests",
            "7",
        ],
    )

    assert result.exit_code == 0
    assert "phases=safety" in result.stdout
    assert "requests=7" in result.stdout
    assert "ceiling=7" in result.stdout
    assert "external_requests=0" in result.stdout


def test_report_cli_generates_separate_files_from_normalized_bundle(
    tmp_path: Path,
) -> None:
    reference = ArtifactReference(
        artifact_id="manifest",
        path="offline-report/manifest.json",
    )
    bundle = ReportBundle(
        run_id="offline-report",
        manifest=reference,
        scope=("offline",),
        exclusions=("live provider",),
        tables=tuple(not_run_table(table_id, reference) for table_id in ReportTableId),
        cost_basis="unknown",
        reproduction_commands=("uv run hcx-eval report --run-id offline-report",),
    )
    bundle_path = tmp_path / "bundle.json"
    _ = bundle_path.write_text(bundle.model_dump_json(), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "report",
            "--run-id",
            "offline-report",
            "--bundle",
            str(bundle_path),
            "--results-root",
            str(tmp_path),
        ],
    )

    report_root = tmp_path / "reports" / "offline-report"
    assert result.exit_code == 0
    assert (report_root / "ACTUAL_TEST_RESULTS.md").is_file()
    assert (report_root / "FINANCIAL_PENSION_MODEL_INSIGHTS.md").is_file()
