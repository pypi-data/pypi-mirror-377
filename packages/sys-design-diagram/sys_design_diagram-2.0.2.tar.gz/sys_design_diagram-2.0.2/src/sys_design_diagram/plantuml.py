"""Copyright (c) 2024, Aydin Abdi.

This module provides a class for generating UML diagrams from PlantUML files.
"""

import asyncio
from pathlib import Path

from sys_design_diagram.exceptions import PlantUMLExecutionError, PlantUMLFileNotFoundError
from sys_design_diagram.interfaces import DiagramInterface
from sys_design_diagram.messages import ErrorMessages
from sys_design_diagram.log import logger

PLANTUML_CMD = "plantuml"


class PlantUMLDiagram(DiagramInterface):
    """PlantUML diagram generator."""

    def __init__(self, puml_file: Path) -> None:
        """Initialize the PlantUML diagram generator.

        Args:
            puml_file: The PlantUML file to generate the diagram from.

        Raises:
            PlantUMLFileNotFoundError: If the PlantUML file does not exist.
        """
        if not isinstance(puml_file, Path):
            raise TypeError(ErrorMessages.NOT_A_PATH.value.format(path=puml_file))
        if not puml_file.exists():
            raise PlantUMLFileNotFoundError(ErrorMessages.FILE_NOT_FOUND.value.format(file_path=puml_file))
        self.puml_file = puml_file

    async def create(self, output_dir: Path) -> None:
        """Generate a diagram from a PlantUML file asynchronously.

        Args:
            output_dir: The directory to save the generated diagram to.

        Raises:
            PlantUMLExecutionError: If the PlantUML command fails to execute.
        """
        if not isinstance(output_dir, Path):
            raise TypeError(ErrorMessages.NOT_A_PATH.value.format(path=output_dir))
        if not output_dir.exists():
            raise ValueError(ErrorMessages.DIRECTORY_NOT_FOUND.value.format(directory_path=output_dir))
        if not output_dir.is_dir():
            raise ValueError(ErrorMessages.NOT_A_DIRECTORY.value.format(directory_path=output_dir))

        cmd = [PLANTUML_CMD, "-o", str(output_dir), str(self.puml_file)]

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        logger.debug(
            f"PlantUML command executed with return code: {process.returncode}, stdout: {stdout.decode().strip()}, stderr: {stderr.decode().strip()}"
        )
        if process.returncode != 0:
            error_message = stderr.decode().strip()
            raise PlantUMLExecutionError(ErrorMessages.PLANTUML_EXECUTION_FAILED.value.format(error=error_message))
