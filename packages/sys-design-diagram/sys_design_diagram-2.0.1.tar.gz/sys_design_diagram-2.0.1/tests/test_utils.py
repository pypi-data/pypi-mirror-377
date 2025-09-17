"""Copyright (c) 2024, Aydin Abdi.

This module contains tests for the utils module in the sys_design_diagram package.
"""

from pathlib import Path
from subprocess import CompletedProcess

import pytest
from sys_design_diagram import utils
from sys_design_diagram.exceptions import DTFDesignError
from sys_design_diagram.messages import ErrorMessages


def test_mkdir_output_creates_directory(tmp_path):
    """Test that mkdir_output creates the directory if it doesn't exist."""
    non_existent_dir = tmp_path / "new_dir"
    result = utils.mkdir_output(str(non_existent_dir))
    assert result.exists(), f"Directory {non_existent_dir} should exist."
    assert result.is_dir(), f"{non_existent_dir} should be a directory."


def test_mkdir_output_exists(tmp_path):
    """Test that mkdir_output does not raise an error if the directory exists."""
    existing_dir = tmp_path / "existing_dir"
    existing_dir.mkdir()
    result = utils.mkdir_output(str(existing_dir))
    assert result.exists(), f"Directory {existing_dir} should exist."
    assert result.is_dir(), f"{existing_dir} should be a directory."


def test_validate_output_path_valid_directory(tmp_path):
    """Test validate_output_path with a valid directory."""
    utils.validate_output_path(tmp_path)


def test_validate_output_path_non_existent_directory():
    """Test validate_output_path with a non-existent directory."""
    non_existent_dir = Path("/non/existent/directory")
    with pytest.raises(
        ValueError, match=ErrorMessages.DIRECTORY_NOT_FOUND.value.format(directory_path=non_existent_dir)
    ):
        utils.validate_output_path(non_existent_dir)


def test_validate_output_path_not_a_directory(tmp_path):
    """Test validate_output_path with a path that is not a directory."""
    not_a_directory = tmp_path / "not_a_directory"
    not_a_directory.touch()
    with pytest.raises(ValueError, match=ErrorMessages.NOT_A_DIRECTORY.value.format(directory_path=not_a_directory)):
        utils.validate_output_path(not_a_directory)


def test_load_module_valid(tmp_path):
    """Test load_module with a valid Python file."""
    module_file = tmp_path / "module.py"
    module_file.write_text("def test_func(): pass")

    module = utils.load_module(module_file)
    assert hasattr(module, "test_func")


def test_load_module_invalid(tmp_path):
    """Test load_module with an invalid Python file."""
    module_file = tmp_path / "invalid_module.py"
    module_file.write_text("def invalid_syntax(: pass")

    with pytest.raises(
        DTFDesignError,
        match=ErrorMessages.MODULE_LOAD_ERROR.value.format(module_path=module_file, error="invalid syntax"),
    ):
        utils.load_module(module_file)


def test_load_module_spec_is_none(tmp_path, mocker):
    """Test load_module with a module that has a None spec."""
    mocker.patch("importlib.util.spec_from_file_location", return_value=None)
    module_file = tmp_path / "module.py"

    with pytest.raises(
        DTFDesignError,
        match=ErrorMessages.MODULE_LOAD_ERROR.value.format(module_path=module_file, error="No spec found"),
    ):
        utils.load_module(module_file)


def test_load_module_spec_has_no_loader(tmp_path, mocker):
    """Test load_module with a module that has a spec with no loader."""
    mocker.patch("importlib.util.spec_from_file_location", return_value=mocker.Mock(loader=None))
    module_file = tmp_path / "module.py"

    with pytest.raises(
        DTFDesignError,
        match=ErrorMessages.MODULE_LOAD_ERROR.value.format(module_path=module_file, error="No loader found"),
    ):
        utils.load_module(module_file)


def test_is_plantuml_installed_success(mocker):
    """Test that PlantUML is installed."""
    plantuml_path = "/usr/local/bin/plantuml"
    mock_run = mocker.patch("sys_design_diagram.utils.run")
    mock_which = mocker.patch("sys_design_diagram.utils.shutil.which", return_value=plantuml_path)
    mock_run.return_value = CompletedProcess(
        args=[plantuml_path, "--version"], returncode=0, stdout=b"PlantUML version 1.2021.0", stderr=b""
    )

    result = utils.is_plantuml_installed()

    mock_which.assert_called_once_with("plantuml")
    mock_run.assert_called_once_with([plantuml_path, "--version"], capture_output=True, check=False)
    assert result is True


def test_is_plantuml_installed_failure(mocker):
    """Test that PlantUML is not installed."""
    mock_run = mocker.patch("sys_design_diagram.utils.run")
    mock_which = mocker.patch("sys_design_diagram.utils.shutil.which", return_value=None)
    mock_run.return_value = CompletedProcess(
        args=["plantuml", "--version"], returncode=1, stdout=b"", stderr=b"plantuml: command not found"
    )

    result = utils.is_plantuml_installed()

    mock_which.assert_called_once_with("plantuml")
    mock_run.assert_not_called()

    assert result is False
