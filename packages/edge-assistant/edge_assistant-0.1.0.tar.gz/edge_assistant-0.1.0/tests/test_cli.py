import sys
from typer.testing import CliRunner

from edge_assistant import cli


def test_help_shows_commands():
    runner = CliRunner()
    result = runner.invoke(cli.app, ["--help"])
    assert result.exit_code == 0
    out = result.output
    # Basic smoke checks for commands we expect
    assert "ask" in out
    assert "research" in out
    assert "kb-index" in out
    assert "edit" in out
