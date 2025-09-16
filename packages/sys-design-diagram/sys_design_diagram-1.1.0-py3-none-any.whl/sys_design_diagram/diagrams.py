"""Copyright (c) 2024, Aydin Abdi.

This module provides a class for generating diagrams using a Python library Diagrams.
"""

from pathlib import Path
from types import ModuleType

from sys_design_diagram import utils
from sys_design_diagram.exceptions import DiagramsExecutionError, DiagramsFileNotFoundError
from sys_design_diagram.interfaces import DiagramInterface
from sys_design_diagram.log import logger
from sys_design_diagram.messages import ErrorMessages


class DiagramsDiagram(DiagramInterface):
    """Diagram generator using a Python module."""

    def __init__(self, diagrams_file: Path) -> None:
        """Initialize the DiagramsDiagram object.

        Args:
            diagrams_file: Path to the Python module containing the diagrams.
        """
        if not isinstance(diagrams_file, Path):
            raise TypeError(ErrorMessages.NOT_A_PATH.value.format(path=diagrams_file))
        if not diagrams_file.exists() or not diagrams_file.is_file():
            raise DiagramsFileNotFoundError(ErrorMessages.FILE_NOT_FOUND.value.format(file_path=diagrams_file))
        self.diagrams_file = diagrams_file

    async def create(self, output_path: Path) -> None:
        """Create diagrams for the design.

        Args:
            output_path: Path to the output directory.
        """
        if not isinstance(output_path, Path):
            raise TypeError(ErrorMessages.NOT_A_PATH.value.format(path=output_path))
        if not output_path.exists():
            raise DiagramsFileNotFoundError(ErrorMessages.DIRECTORY_NOT_FOUND.value.format(directory_path=output_path))
        if not output_path.is_dir():
            raise DiagramsFileNotFoundError(ErrorMessages.NOT_A_DIRECTORY.value.format(directory_path=output_path))
        utils.validate_output_path(output_path)
        try:
            module = utils.load_module(self.diagrams_file)
            logger.info(f"Loaded module from directory: {self.diagrams_file.parent}, file: {self.diagrams_file.name}")
        except Exception as module_error:
            raise DiagramsExecutionError(
                ErrorMessages.DIAGRAMS_EXECUTION_FAILED.value.format(
                    module_name=self.diagrams_file.stem, error=module_error
                )
            ) from module_error
        await self._execute_component_diagram(module, output_path)

    async def _execute_component_diagram(self, module: ModuleType, output_path: Path) -> None:
        """Execute the component_diagram function from the module.

        Args:
            module: The loaded module containing the component_diagram function.
            output_path: Path to the output directory.

        Raises:
            DiagramExecutionError: If the component_diagram function is not found or fails to execute.
        """
        component_diagram = getattr(module, "component_diagram", None)
        if component_diagram is None:
            raise DiagramsExecutionError(
                ErrorMessages.MODULE_NOT_FOUND.value.format(module_name=self.diagrams_file.stem)
            )

        output_diagram_path = output_path / f"{self.diagrams_file.stem}"
        try:
            logger.info(f"Executing component_diagram function from {self.diagrams_file.stem} module.")
            component_diagram(str(output_diagram_path))
            logger.info(f"Successfully executed component_diagram function from {self.diagrams_file.stem} module.")
        except Exception as diagrams_error:
            raise DiagramsExecutionError(
                ErrorMessages.DIAGRAMS_EXECUTION_FAILED.value.format(
                    module_name=self.diagrams_file.stem, error=diagrams_error
                )
            ) from diagrams_error
