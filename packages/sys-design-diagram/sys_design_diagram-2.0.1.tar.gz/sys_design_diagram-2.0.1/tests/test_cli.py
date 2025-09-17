"""Copyright (c) 2024, Aydin Abdi.

This module contains the tests for the CLI commands.
"""

import pytest
import os
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


def test_env_var_designs_dir(monkeypatch, runner, tmp_path, mock_process_diagrams):
    """Test resolving designs dir from environment variable when -d omitted."""
    designs_dir = tmp_path / "env_designs"
    designs_dir.mkdir()
    monkeypatch.setenv("SDD_DESIGNS_DIR", str(designs_dir))
    result = runner.invoke(cli, ["plantuml"])  # no -d provided
    assert result.exit_code == 0
    default_output_dir = Path.cwd() / "sys-design-diagram-output"
    mock_process_diagrams.run.assert_called_once_with(
        mock_process_diagrams.process_plantumls, designs_dir, default_output_dir
    )


def test_env_var_output_dir(monkeypatch, runner, temp_designs_dir, mock_process_diagrams, tmp_path):
    """Test resolving output dir from environment variable when -o omitted."""
    out_dir = tmp_path / "env_out"
    monkeypatch.setenv("SDD_OUTPUT_DIR", str(out_dir))
    result = runner.invoke(cli, ["plantuml", "-d", str(temp_designs_dir)])
    assert result.exit_code == 0
    mock_process_diagrams.run.assert_called_once_with(
        mock_process_diagrams.process_plantumls, temp_designs_dir, out_dir
    )


def test_conventional_designs_dir(monkeypatch, runner, mock_process_diagrams, tmp_path):
    """Test using ./designs conventional directory when present and -d omitted."""
    # Create a temporary cwd with a designs folder
    designs_dir = tmp_path / "designs"
    designs_dir.mkdir()

    # Change directory to tmp_path so CLI discovers ./designs automatically
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(cli, ["plantuml"])  # no -d provided
        assert result.exit_code == 0
        default_output_dir = tmp_path / "sys-design-diagram-output"
        mock_process_diagrams.run.assert_called_once_with(
            mock_process_diagrams.process_plantumls, designs_dir, default_output_dir
        )
    finally:
        os.chdir(original_cwd)


def test_explicit_output_overrides_env(monkeypatch, runner, temp_designs_dir, mock_process_diagrams, tmp_path):
    """Explicit -o should override SDD_OUTPUT_DIR env var (covers explicit output branch)."""
    env_out = tmp_path / "env_out"
    monkeypatch.setenv("SDD_OUTPUT_DIR", str(env_out))
    explicit_out = tmp_path / "explicit_out"
    result = runner.invoke(cli, ["plantuml", "-d", str(temp_designs_dir), "-o", str(explicit_out)])
    assert result.exit_code == 0
    mock_process_diagrams.run.assert_called_once_with(
        mock_process_diagrams.process_plantumls, temp_designs_dir, explicit_out
    )


def test_explicit_designs_dir_no_env(monkeypatch, runner, temp_designs_dir, mock_process_diagrams, tmp_path):
    """Providing -d directly without env or conventional fallback (covers direct designs branch)."""
    # Ensure env var not set and no ./designs in cwd influencing result
    monkeypatch.delenv("SDD_DESIGNS_DIR", raising=False)
    result = runner.invoke(cli, ["plantuml", "-d", str(temp_designs_dir)])
    assert result.exit_code == 0
    expected_output = Path.cwd() / "sys-design-diagram-output"
    mock_process_diagrams.run.assert_called_once_with(
        mock_process_diagrams.process_plantumls, temp_designs_dir, expected_output
    )


def test_missing_designs_dir_error(monkeypatch, runner, tmp_path):
    """Error when no -d, no env var, and no ./designs directory (covers not-provided branch)."""
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(cli, ["plantuml"])  # nothing provided
        assert result.exit_code != 0
        assert "Designs directory not provided" in result.output
    finally:
        os.chdir(original_cwd)


def test_conventional_designs_is_file(monkeypatch, runner, tmp_path):
    """If ./designs exists but is a file, still treat as missing (covers exists & not dir branch)."""
    designs_file = tmp_path / "designs"
    designs_file.write_text("not a directory")
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(cli, ["plantuml"])  # no -d
        assert result.exit_code != 0
        assert "Designs directory not provided" in result.output
    finally:
        os.chdir(original_cwd)


def test_env_var_designs_dir_missing(monkeypatch, runner):
    """When SDD_DESIGNS_DIR points to a non-existent path, should error (covers not exists raise)."""
    missing = Path.cwd() / "__definitely_missing_dir__"
    if missing.exists():  # safety cleanup edge case
        raise AssertionError("Sentinel path unexpectedly exists; choose different name")
    monkeypatch.setenv("SDD_DESIGNS_DIR", str(missing))
    result = runner.invoke(cli, ["plantuml"])  # no -d; env var used
    assert result.exit_code != 0
    assert f"'{missing}' does not exist" in result.output
