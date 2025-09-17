"""Copyright (c) 2024, Aydin Abdi.

This module contains tests for the DiagramsDiagram class in the sys_design_diagram.diagrams module.
"""

from pathlib import Path

import pytest
from sys_design_diagram.diagrams import DiagramsDiagram
from sys_design_diagram.exceptions import DiagramsExecutionError, DiagramsFileNotFoundError
from sys_design_diagram.messages import ErrorMessages


@pytest.mark.asyncio
async def test_init_valid_file(setup_design_dirs):
    """Test initializing DiagramsDiagram with a valid file."""
    diagrams_file = setup_design_dirs / "design_1" / "diagrams_component.py"
    diagram = DiagramsDiagram(diagrams_file)
    assert diagram.diagrams_file == diagrams_file


@pytest.mark.asyncio
async def test_init_invalid_file(setup_design_dirs):
    """Test initializing DiagramsDiagram with an invalid file."""
    invalid_file = setup_design_dirs / "design_1" / "non_existent.py"
    with pytest.raises(
        DiagramsFileNotFoundError, match=ErrorMessages.FILE_NOT_FOUND.value.format(file_path=invalid_file)
    ):
        DiagramsDiagram(invalid_file)


@pytest.mark.asyncio
async def test_init_not_a_path():
    """Test initializing DiagramsDiagram with a non-path type."""
    with pytest.raises(TypeError, match=ErrorMessages.NOT_A_PATH.value.format(path="invalid_file")):
        DiagramsDiagram("invalid_file")


@pytest.mark.asyncio
async def test_create_valid(setup_design_dirs, output_dir):
    """Test creating diagrams with a valid component_diagram function."""
    diagrams_file = setup_design_dirs / "design_1" / "diagrams_component.py"
    diagram = DiagramsDiagram(diagrams_file)
    await diagram.create(output_dir)
    output_file = output_dir / "diagrams_component.png"
    assert output_file.exists()


@pytest.mark.asyncio
async def test_create_invalid_output_dir(setup_design_dirs):
    """Test creating diagrams with an invalid output directory."""
    diagrams_file = setup_design_dirs / "design_1" / "diagrams_component.py"
    diagram = DiagramsDiagram(diagrams_file)
    invalid_output_dir = "invalid_output_dir"
    with pytest.raises(TypeError, match=ErrorMessages.NOT_A_PATH.value.format(path=invalid_output_dir)):
        await diagram.create(invalid_output_dir)


@pytest.mark.asyncio
async def test_create_output_dir_not_exists(setup_design_dirs):
    """Test creating diagrams when output directory does not exist."""
    diagrams_file = setup_design_dirs / "design_1" / "diagrams_component.py"
    diagram = DiagramsDiagram(diagrams_file)
    non_existent_output_dir = Path("non_existent_output_dir")
    with pytest.raises(
        DiagramsFileNotFoundError,
        match=ErrorMessages.DIRECTORY_NOT_FOUND.value.format(directory_path=non_existent_output_dir),
    ):
        await diagram.create(non_existent_output_dir)


@pytest.mark.asyncio
async def test_create_output_dir_not_a_directory(setup_design_dirs, tmp_path):
    """Test creating diagrams when output directory is not a directory."""
    diagrams_file = setup_design_dirs / "design_1" / "diagrams_component.py"
    diagram = DiagramsDiagram(diagrams_file)
    not_a_directory = tmp_path / "not_a_directory.txt"
    not_a_directory.write_text("This is a file, not a directory.")
    with pytest.raises(
        DiagramsFileNotFoundError, match=ErrorMessages.NOT_A_DIRECTORY.value.format(directory_path=not_a_directory)
    ):
        await diagram.create(not_a_directory)


@pytest.mark.asyncio
async def test_execute_component_diagram_not_found(setup_design_dirs, output_dir):
    """Test _execute_component_diagram method when component_diagram is not found."""
    diagrams_file = setup_design_dirs / "design_1" / "invalid_component.py"
    diagram = DiagramsDiagram(diagrams_file)
    with pytest.raises(
        DiagramsExecutionError,
        match=ErrorMessages.MODULE_NOT_FOUND.value.format(module_name="invalid_component"),
    ):
        await diagram.create(output_dir)


@pytest.mark.asyncio
async def test_execute_component_diagram_error(setup_design_dirs, output_dir):
    """Test _execute_component_diagram method with a failing component_diagram function."""
    diagrams_file = setup_design_dirs / "design_1" / "broken_component.py"
    diagram = DiagramsDiagram(diagrams_file)

    with pytest.raises(
        DiagramsExecutionError,
        match=ErrorMessages.DIAGRAMS_EXECUTION_FAILED.value.format(module_name=diagrams_file.stem, error="*"),
    ):
        await diagram.create(output_dir)


@pytest.mark.asyncio
async def test_execute_component_diagram_exception(setup_design_dirs, output_dir):
    """Test _execute_component_diagram method with an exception in component_diagram function."""
    diagrams_file = setup_design_dirs / "design_1" / "exception_component.py"
    diagram = DiagramsDiagram(diagrams_file)

    with pytest.raises(
        DiagramsExecutionError,
        match=ErrorMessages.DIAGRAMS_EXECUTION_FAILED.value.format(
            module_name=diagrams_file.stem, error="This is an exception"
        ),
    ):
        await diagram.create(output_dir)
