"""Copyright (c) 2024, Aydin Abdi.

This module is test for process_diagrams.py module.
"""

import asyncio

import pytest
from sys_design_diagram.exceptions import DiagramsExecutionError, MermaidExecutionError, PlantUMLExecutionError
from sys_design_diagram.process_diagrams import ProcessDiagrams


@pytest.mark.asyncio
async def test_process_plantumls(setup_design_dirs, output_dir):
    """Test processing PlantUML diagrams."""
    await ProcessDiagrams.process_plantumls(setup_design_dirs, output_dir)
    assert (output_dir / "design_1" / "1.png").exists()
    assert (output_dir / "design_1" / "2.png").exists()
    assert (output_dir / "design_2" / "1.png").exists()
    assert (output_dir / "design_2" / "2.png").exists()


@pytest.mark.asyncio
async def test_process_diagrams(setup_design_dirs, output_dir):
    """Test processing component diagrams."""
    await ProcessDiagrams.process_diagrams(setup_design_dirs, output_dir)
    assert (output_dir / "design_1" / "diagrams_component.png").exists()
    assert (output_dir / "design_2" / "diagrams_component.png").exists()


@pytest.mark.asyncio
async def test_process_mermaids(setup_design_dirs, output_dir):
    """Test processing Mermaid diagrams."""
    await ProcessDiagrams.process_mermaids(setup_design_dirs, output_dir)
    assert (output_dir / "design_1" / "test1.png").exists()
    assert (output_dir / "design_1" / "test2.png").exists()
    assert (output_dir / "design_2" / "test3.png").exists()


@pytest.mark.asyncio
async def test_process_all(setup_design_dirs, output_dir):
    """Test processing all diagrams."""
    await ProcessDiagrams.process_all(setup_design_dirs, output_dir)
    assert (output_dir / "design_1" / "1.png").exists()
    assert (output_dir / "design_1" / "2.png").exists()
    assert (output_dir / "design_2" / "1.png").exists()
    assert (output_dir / "design_2" / "2.png").exists()
    assert (output_dir / "design_1" / "diagrams_component.png").exists()
    assert (output_dir / "design_2" / "diagrams_component.png").exists()
    # Check Mermaid files are also processed
    assert (output_dir / "design_1" / "test1.png").exists()
    assert (output_dir / "design_1" / "test2.png").exists()
    assert (output_dir / "design_2" / "test3.png").exists()


@pytest.mark.asyncio
async def test_process_plantumls_exception(mocker, setup_design_dirs, output_dir):
    """Test exception handling in process_plantumls."""
    mocker.patch(
        "sys_design_diagram.plantuml.PlantUMLDiagram.create",
        side_effect=PlantUMLExecutionError("Mocked PlantUML error"),
    )
    await ProcessDiagrams.process_plantumls(setup_design_dirs, output_dir)
    assert not (output_dir / "design_1" / "1.png").exists()


@pytest.mark.asyncio
async def test_process_diagrams_exception(mocker, setup_design_dirs, output_dir):
    """Test exception handling in process_diagrams."""
    mocker.patch(
        "sys_design_diagram.diagrams.DiagramsDiagram.create",
        side_effect=DiagramsExecutionError("Mocked Diagrams error"),
    )
    await ProcessDiagrams.process_diagrams(setup_design_dirs, output_dir)
    assert not (output_dir / "design_1" / "diagrams_component.png").exists()


@pytest.mark.asyncio
async def test_process_plantumls_iterdir_exception(mocker, setup_design_dirs, output_dir):
    """Test exception handling in process_plantumls when iterating directories."""
    mocker.patch("pathlib.Path.iterdir", side_effect=Exception("Mocked iterdir error"))
    await ProcessDiagrams.process_plantumls(setup_design_dirs, output_dir)


@pytest.mark.asyncio
async def test_process_mermaids_exception(mocker, setup_design_dirs, output_dir):
    """Test exception handling in process_mermaids."""
    mocker.patch(
        "sys_design_diagram.mermaid.MermaidDiagram.create",
        side_effect=MermaidExecutionError("Mocked Mermaid error"),
    )
    await ProcessDiagrams.process_mermaids(setup_design_dirs, output_dir)
    assert not (output_dir / "design_1" / "test1.png").exists()


@pytest.mark.asyncio
async def test_process_diagrams_iterdir_exception(mocker, setup_design_dirs, output_dir):
    """Test exception handling in process_diagrams when iterating directories."""
    mocker.patch("pathlib.Path.iterdir", side_effect=Exception("Mocked iterdir error"))
    await ProcessDiagrams.process_diagrams(setup_design_dirs, output_dir)


@pytest.mark.asyncio
async def test_process_mermaids_iterdir_exception(mocker, setup_design_dirs, output_dir):
    """Test exception handling in process_mermaids when iterating directories."""
    mocker.patch("pathlib.Path.iterdir", side_effect=Exception("Mocked iterdir error"))
    await ProcessDiagrams.process_mermaids(setup_design_dirs, output_dir)


async def coro_func() -> None:
    """Test coroutine function."""
    await asyncio.sleep(0.1)


def test_run():
    """Test run method."""
    result = ProcessDiagrams.run(coro_func)
    assert result is None
