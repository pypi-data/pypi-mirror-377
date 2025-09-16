"""Copyright (c) 2024, Aydin Abdi.

This module contains fixtures for testing the design module.
"""

import shutil
from pathlib import Path
from typing import Generator

import pytest

from loguru import logger
from _pytest.logging import LogCaptureFixture


OUTPUT_DIR = "design-output"
DESIGN_DIR = "design-diagrams"
VALID_COMPONENT_DIAGRAM = """
from diagrams import Diagram
from diagrams.aws.compute import EC2


def component_diagram(output_path: str):
    with Diagram('Test Diagram', show=False, filename=output_path):
        EC2('Instance')
"""

INVALID_COMPONENT_DIAGRAM = """
from diagrams import Diagram
from diagrams.aws.compute import EC2


def some_other_function(output_path: str):
    with Diagram('Test Diagram', show=False, filename=output_path):
        EC2('Instance')
"""

BROKEN_COMPONENT_DIAGRAM = """
from diagrams import Diagram
from diagrams.aws.compute import EC2


def component_diagram(output_path: str):
    with Diagram('Test Diagram', show=False, filename=output_path):
        EC2('Instance'
"""

EXCEPTION_COMPONENT_DIAGRAM = """
from diagrams import Diagram
from diagrams.aws.compute import EC2


def component_diagram(output_path: str):
    raise RuntimeError('This is an exception')
"""

DESIGN_1_FILES = [
    ("1.puml", "@startuml\nBob -> Alice : hello\n@enduml"),
    ("2.puml", "@startuml\nAlice -> Bob : hi\n@enduml"),
    (
        "diagrams_component.py",
        VALID_COMPONENT_DIAGRAM,
    ),
    (
        "invalid_component.py",
        INVALID_COMPONENT_DIAGRAM,
    ),
    (
        "broken_component.py",
        BROKEN_COMPONENT_DIAGRAM,
    ),
    (
        "exception_component.py",
        EXCEPTION_COMPONENT_DIAGRAM,
    ),
    ("test1.mmd", "graph TD\n    A[Start] --> B{Is it?}\n    B -->|Yes| C[OK]\n    B -->|No| D[End]"),
    ("test2.mmd", "sequenceDiagram\n    A->>B: Hello\n    B-->>A: Hi"),
]

DESIGN_2_FILES = [
    ("1.puml", "@startuml\nA -> B : test\n@enduml"),
    ("2.puml", "@startuml\nB -> A : reply\n@enduml"),
    (
        "diagrams_component.py",
        VALID_COMPONENT_DIAGRAM,
    ),
    ("test3.mmd", "graph LR\n    A[Square] --> B((Circle))"),
]


@pytest.fixture(scope="session")
def setup_design_dirs(tmp_path_factory: pytest.TempPathFactory) -> Generator[Path, None, None]:
    """Setup temporary design directories and files for testing asynchronously.

    It creates temporary design_diagrams directory with two design directories and PlantUML and Python files.
    After the test, it cleans up the temporary directories.
    """
    designs_dir = tmp_path_factory.mktemp(DESIGN_DIR)
    design_1 = designs_dir / "design_1"
    design_2 = designs_dir / "design_2"
    design_1.mkdir(parents=True, exist_ok=True)
    design_2.mkdir(parents=True, exist_ok=True)

    design_files = {
        design_1: DESIGN_1_FILES,
        design_2: DESIGN_2_FILES,
    }

    # Create design files
    for design, files in design_files.items():
        for file_name, content in files:
            (design / file_name).write_text(content)

    yield designs_dir

    # Teardown: Clean up the temporary directories
    shutil.rmtree(designs_dir, ignore_errors=True)


@pytest.fixture
def output_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture for output directory."""
    output_dir = tmp_path / OUTPUT_DIR
    output_dir.mkdir()
    yield output_dir
    # Teardown: Clean up the output directory
    shutil.rmtree(output_dir, ignore_errors=True)


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    """Custom fixture to capture logs with loguru."""
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,  # Set to 'True' if your test is spawning child processes.
    )
    yield caplog
    logger.remove(handler_id)
