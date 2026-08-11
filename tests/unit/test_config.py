from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from hcx_eval.config import HarnessSettings, load_settings


def test_settings_default_to_offline_when_no_key_or_budget(tmp_path: Path) -> None:
    # Given: valid local source roots and no execution approval.
    data_root = tmp_path / "data"
    docs_root = tmp_path / "docs"
    data_root.mkdir()
    docs_root.mkdir()

    # When: settings are constructed with their network defaults.
    settings = HarnessSettings(data_root=data_root, naver_docs_root=docs_root)

    # Then: execution is disabled and no request budget exists.
    assert (settings.execute, settings.max_requests_per_run) == (False, 0)


@pytest.mark.parametrize(("request_budget", "token_budget"), [(0, 1), (1, 0)])
def test_settings_reject_execution_without_positive_budgets(
    tmp_path: Path, request_budget: int, token_budget: int
) -> None:
    # Given: explicit execution approval with one missing positive ceiling.
    data_root = tmp_path / "data"
    docs_root = tmp_path / "docs"
    data_root.mkdir()
    docs_root.mkdir()

    # When / Then: validation fails before a network client can be built.
    with pytest.raises(ValidationError):
        _ = HarnessSettings(
            execute=True,
            clova_studio_api_key=SecretStr("secret"),
            max_requests_per_run=request_budget,
            max_tokens_per_run=token_budget,
            data_root=data_root,
            naver_docs_root=docs_root,
        )


def test_settings_reject_execution_without_key(tmp_path: Path) -> None:
    # Given: positive ceilings but no API key.
    data_root = tmp_path / "data"
    docs_root = tmp_path / "docs"
    data_root.mkdir()
    docs_root.mkdir()

    # When / Then: live execution cannot be enabled.
    with pytest.raises(ValidationError):
        _ = HarnessSettings(
            execute=True,
            max_requests_per_run=1,
            max_tokens_per_run=1,
            data_root=data_root,
            naver_docs_root=docs_root,
        )


def test_yaml_load_resolves_paths_and_environment_wins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: a YAML file with relative roots and a distinct env concurrency.
    (tmp_path / "data").mkdir()
    (tmp_path / "docs").mkdir()
    config_path = tmp_path / "settings.yaml"
    _ = config_path.write_text(
        "data_root: data\nnaver_docs_root: docs\nmax_concurrency: 2\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("MAX_CONCURRENCY", "7")

    # When: the settings boundary loads both sources.
    settings = load_settings(config_path)

    # Then: paths are relative to the YAML and environment has precedence.
    assert settings.data_root == (tmp_path / "data").resolve()
    assert settings.max_concurrency == 7


def test_malformed_yaml_is_rejected(tmp_path: Path) -> None:
    # Given: a YAML sequence where a settings mapping is required.
    config_path = tmp_path / "bad.yaml"
    _ = config_path.write_text("- invalid\n", encoding="utf-8")

    # When / Then: the malformed boundary is rejected.
    with pytest.raises(ValueError, match="cannot load configuration"):
        _ = load_settings(config_path)


def test_invalid_concurrency_is_rejected(tmp_path: Path) -> None:
    # Given: an impossible worker count.
    data_root = tmp_path / "data"
    docs_root = tmp_path / "docs"
    data_root.mkdir()
    docs_root.mkdir()

    # When / Then: validation rejects it.
    with pytest.raises(ValidationError):
        _ = HarnessSettings(
            max_concurrency=0, data_root=data_root, naver_docs_root=docs_root
        )
