"""Copyright (c) 2024, Aydin Abdi.

This module is used to generate diagrams from the design files.
"""

import asyncio
from pathlib import Path
from typing import Any, Callable, Coroutine, TypeVar

from sys_design_diagram.diagrams import DiagramsDiagram
from sys_design_diagram.log import logger
from sys_design_diagram.mermaid import MermaidDiagram
from sys_design_diagram.plantuml import PlantUMLDiagram

T = TypeVar("T")


class ProcessDiagrams:
    """Factory class for processing diagrams."""

    @staticmethod
    async def process_plantumls(designs_dir: Path, output_dir: Path) -> None:
        """Process PlantUML diagrams in the given directory.

        Args:
            designs_dir: The directory containing the PlantUML diagrams.
            output_dir: The directory to output the diagrams.
        """
        tasks = []
        try:
            for design_dir in designs_dir.iterdir():
                for uml_file in design_dir.glob("*.puml"):
                    # Create a directory for each design directory in current directory
                    current_dir = Path.cwd()
                    output_file_path = current_dir / output_dir / design_dir.name
                    output_file_path.mkdir(parents=True, exist_ok=True)
                    diagram = PlantUMLDiagram(uml_file)
                    tasks.append(ProcessDiagrams._run_task(diagram.create, output_file_path))
        except Exception as e:
            logger.error(f"Error processing PlantUML diagrams: {e}")
        await asyncio.gather(*tasks)

    @staticmethod
    async def process_diagrams(designs_dir: Path, output_dir: Path) -> None:
        """Process component diagrams in the given directory.

        Args:
            designs_dir: The directory containing the component diagrams.
            output_dir: The directory to output the diagrams.
        """
        tasks = []
        try:
            for design_dir in designs_dir.iterdir():
                for py_file in design_dir.glob("*.py"):
                    output_file_path = output_dir / design_dir.name
                    output_file_path.mkdir(parents=True, exist_ok=True)
                    diagram = DiagramsDiagram(py_file)
                    tasks.append(ProcessDiagrams._run_task(diagram.create, output_file_path))
        except Exception as e:
            logger.error(f"Error processing component diagrams: {e}")
        await asyncio.gather(*tasks)

    @staticmethod
    async def process_mermaids(designs_dir: Path, output_dir: Path) -> None:
        """Process Mermaid diagrams in the given directory.

        Args:
            designs_dir: The directory containing the Mermaid diagrams.
            output_dir: The directory to output the diagrams.
        """
        tasks = []
        try:
            for design_dir in designs_dir.iterdir():
                for mermaid_file in design_dir.glob("*.mmd"):
                    # Create a directory for each design directory in current directory
                    current_dir = Path.cwd()
                    output_file_path = current_dir / output_dir / design_dir.name
                    output_file_path.mkdir(parents=True, exist_ok=True)
                    diagram = MermaidDiagram(mermaid_file)
                    tasks.append(ProcessDiagrams._run_task(diagram.create, output_file_path))
        except Exception as e:
            logger.error(f"Error processing Mermaid diagrams: {e}")
        await asyncio.gather(*tasks)

    @staticmethod
    async def process_all(designs_dir: Path, output_dir: Path) -> None:
        """Process all diagrams in the given directory.

        Args:
            designs_dir: The directory containing the diagrams.
            output_dir: The directory to output the diagrams
        """
        await ProcessDiagrams.process_plantumls(designs_dir, output_dir)
        await ProcessDiagrams.process_diagrams(designs_dir, output_dir)
        await ProcessDiagrams.process_mermaids(designs_dir, output_dir)

    @staticmethod
    async def _run_task(task: Callable[..., Coroutine[Any, Any, T]], *args: Any, **kwargs: Any) -> None:
        """Run a task and handle exceptions gracefully.

        Args:
            task: The task to run.
            args: The arguments to pass to the task.
            kwargs: The keyword arguments to pass to the task
        """
        try:
            await task(*args, **kwargs)
        except Exception as e:
            logger.error(f"Task failed with error: {e}")

    @staticmethod
    def run(coro_func: Callable[..., Coroutine[Any, Any, T]], *args: Any, **kwargs: Any) -> None:
        """Run the given coroutine function with the given arguments.

        Args:
            coro_func: The coroutine function to run.
            args: The arguments to pass to the coroutine function.
            kwargs: The keyword arguments to pass to the coroutine function.
        """
        asyncio.run(coro_func(*args, **kwargs))
