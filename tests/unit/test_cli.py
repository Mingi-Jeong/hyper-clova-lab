import socket
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
