"""Copyright (c) 2024, Aydin Abdi.

This module contains the tests for the CLI commands.
"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from sys_design_diagram.cli import cli


@pytest.fixture
def runner():
    """Fixture for invoking CLI commands."""
    return CliRunner()


@pytest.fixture
def mock_process_diagrams(mocker):
    """Fixture for mocking the ProcessDiagrams class."""
    return mocker.patch("sys_design_diagram.cli.ProcessDiagrams")


@pytest.fixture
def temp_designs_dir(tmp_path):
    """Fixture for creating a temporary directory for designs."""
    designs_dir = tmp_path / "designs"
    designs_dir.mkdir()
    return designs_dir


def test_cli_version(runner):
    """Test the CLI version command."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "System Design Diagram Generator" in result.output


def test_cli_help(runner):
    """Test the CLI help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Command line interface for the sys-design-diagram package" in result.output


@pytest.mark.parametrize("command", ["plantuml", "diagrams", "mermaid", "process-all"])
def test_subcommand_help(runner, command):
    """Test the help command for subcommands."""
    result = runner.invoke(cli, [command, "--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


@pytest.mark.parametrize(
    "command,process_method",
    [
        ("plantuml", "process_plantumls"),
        ("diagrams", "process_diagrams"),
        ("mermaid", "process_mermaids"),
        ("process-all", "process_all"),
    ],
)
def test_diagram_commands(mocker, runner, temp_designs_dir, mock_process_diagrams, command, process_method):
    """Test the diagram commands."""
    output_dir = temp_designs_dir.parent / "output"
    result = runner.invoke(cli, [command, "-d", str(temp_designs_dir), "-o", str(output_dir)])

    assert result.exit_code == 0
    mock_process_diagrams.run.assert_called_once_with(
        getattr(mock_process_diagrams, process_method), temp_designs_dir, output_dir
    )


def test_verbose_mode(mocker, runner, temp_designs_dir):
    """Test the verbose mode."""
    mock_configure_logging = mocker.patch("sys_design_diagram.cli.configure_logging")
    mock_process_diagrams = mocker.patch("sys_design_diagram.cli.ProcessDiagrams.run")
    result = runner.invoke(cli, ["-v", "plantuml", "-d", str(temp_designs_dir), "-o", "output"])
    assert result.exit_code == 0
    mock_configure_logging.assert_called_once_with(verbose=True)


def test_invalid_designs_dir(runner):
    """Test the case where the designs directory does not exist."""
    result = runner.invoke(cli, ["plantuml", "-d", "/non/existent/path", "-o", "output"])
    assert result.exit_code != 0
    assert "Directory" in result.output and "does not exist" in result.output


def test_default_output_dir(runner, temp_designs_dir, mock_process_diagrams):
    """Test the case where the output directory is not provided."""
    default_output_dir = Path.cwd() / "sys-design-diagram-output"
    result = runner.invoke(cli, ["plantuml", "-d", str(temp_designs_dir)])
    assert result.exit_code == 0
    mock_process_diagrams.run.assert_called_once_with(
        mock_process_diagrams.process_plantumls, temp_designs_dir, default_output_dir
    )
