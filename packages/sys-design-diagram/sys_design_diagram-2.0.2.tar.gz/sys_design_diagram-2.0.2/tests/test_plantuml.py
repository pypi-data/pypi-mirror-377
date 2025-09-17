"""Copyright (c) 2024, Aydin Abdi.

This module contains tests for the PlantUMLDiagram class in the sys_design_diagram.plantuml module.
"""

import pytest
from sys_design_diagram.exceptions import PlantUMLExecutionError, PlantUMLFileNotFoundError
from sys_design_diagram.messages import ErrorMessages
from sys_design_diagram.plantuml import PlantUMLDiagram


@pytest.mark.asyncio
async def test_init_valid_file(setup_design_dirs):
    """Test initializing PlantUMLDiagram with a valid file."""
    puml_file = setup_design_dirs / "design_1" / "1.puml"
    diagram = PlantUMLDiagram(puml_file)
    assert diagram.puml_file == puml_file


@pytest.mark.asyncio
async def test_init_invalid_file(setup_design_dirs):
    """Test initializing PlantUMLDiagram with an invalid file."""
    invalid_file = setup_design_dirs / "design_1" / "non_existent.puml"
    with pytest.raises(
        PlantUMLFileNotFoundError, match=ErrorMessages.FILE_NOT_FOUND.value.format(file_path=invalid_file)
    ):
        PlantUMLDiagram(invalid_file)


@pytest.mark.asyncio
async def test_init_not_a_path():
    """Test initializing PlantUMLDiagram with a non-path type."""
    with pytest.raises(TypeError, match=ErrorMessages.NOT_A_PATH.value.format(path="invalid_file")):
        PlantUMLDiagram("invalid_file")


@pytest.mark.asyncio
async def test_create_valid(setup_design_dirs, output_dir):
    """Test creating a diagram with a valid PlantUML file."""
    puml_file = setup_design_dirs / "design_1" / "1.puml"
    diagram = PlantUMLDiagram(puml_file)
    await diagram.create(output_dir)
    output_file = output_dir / "1.png"
    assert output_file.exists()


@pytest.mark.asyncio
async def test_create_not_a_path(setup_design_dirs):
    """Test create method with non-path output directory."""
    puml_file = setup_design_dirs / "design_1" / "1.puml"
    diagram = PlantUMLDiagram(puml_file)
    with pytest.raises(TypeError, match=ErrorMessages.NOT_A_PATH.value.format(path="/invalid/output/dir")):
        await diagram.create("/invalid/output/dir")


@pytest.mark.asyncio
async def test_create_directory_not_found(setup_design_dirs, output_dir):
    """Test create method with non-existent output directory."""
    puml_file = setup_design_dirs / "design_1" / "1.puml"
    diagram = PlantUMLDiagram(puml_file)
    non_existent_dir = output_dir / "non_existent"
    with pytest.raises(
        ValueError, match=ErrorMessages.DIRECTORY_NOT_FOUND.value.format(directory_path=non_existent_dir)
    ):
        await diagram.create(non_existent_dir)


@pytest.mark.asyncio
async def test_create_not_a_directory(setup_design_dirs, output_dir):
    """Test create method with output directory that is not a directory."""
    puml_file = setup_design_dirs / "design_1" / "1.puml"
    diagram = PlantUMLDiagram(puml_file)
    non_directory_path = output_dir / "not_a_directory"
    non_directory_path.touch()  # Create a file, not a directory
    with pytest.raises(ValueError, match=ErrorMessages.NOT_A_DIRECTORY.value.format(directory_path=non_directory_path)):
        await diagram.create(non_directory_path)


@pytest.mark.asyncio
async def test_create_execution_failure(setup_design_dirs, output_dir, mocker):
    """Test create method with PlantUML command execution failure."""
    puml_file = setup_design_dirs / "design_1" / "1.puml"
    diagram = PlantUMLDiagram(puml_file)

    mock_subprocess = mocker.patch("sys_design_diagram.plantuml.asyncio.create_subprocess_exec")
    mock_process = mocker.MagicMock()
    mock_process.communicate = mocker.AsyncMock(return_value=(b"", b"Mocked command failure"))
    mock_process.returncode = 1
    mock_subprocess.return_value = mock_process

    with pytest.raises(
        PlantUMLExecutionError,
        match=ErrorMessages.PLANTUML_EXECUTION_FAILED.value.format(error="Mocked command failure"),
    ):
        await diagram.create(output_dir)
