"""Copyright (c) 2024, Aydin Abdi.

This module contains utility functions for the sys-design-diagram package.
"""

import importlib.util
import shutil
from pathlib import Path
from subprocess import run
from types import ModuleType
from typing import Optional

from sys_design_diagram.exceptions import DTFDesignError
from sys_design_diagram.log import logger
from sys_design_diagram.messages import ErrorMessages


def mkdir_output(output_dir: str) -> Path:
    """Create the output directory if it does not exist.

    Args:
        output_dir: The path to the output directory.

    Returns:
        A Path object pointing to the output directory.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def validate_output_path(output_path: Path) -> None:
    """Validate the output directory path.

    Args:
        output_path: Path to the output directory.

    Raises:
        ValueError: If the output directory does not exist or is not a directory.
    """
    if not output_path.exists():
        raise ValueError(ErrorMessages.DIRECTORY_NOT_FOUND.value.format(directory_path=output_path))
    if not output_path.is_dir():
        raise ValueError(ErrorMessages.NOT_A_DIRECTORY.value.format(directory_path=output_path))


def load_module(file_path: Path) -> ModuleType:
    """Load the module from the file path.

    Args:
        file_path: Path to the Python file.

    Returns:
        The loaded module.

    Raises:
        DTFDesignError: If the module cannot be loaded.
    """
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    if spec is None:
        raise DTFDesignError(ErrorMessages.MODULE_LOAD_ERROR.value.format(module_path=file_path, error="No spec found"))
    if spec.loader is None:
        raise DTFDesignError(
            ErrorMessages.MODULE_LOAD_ERROR.value.format(module_path=file_path, error="No loader found")
        )
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        raise DTFDesignError(ErrorMessages.MODULE_LOAD_ERROR.value.format(module_path=file_path, error=e)) from e
    else:
        return module


def is_plantuml_installed() -> bool:
    """Check if PlantUML is installed on the system.

    Returns:
        True if PlantUML is installed, otherwise False.
    """
    plantuml_path = shutil.which("plantuml")
    if plantuml_path is None:
        return False

    process = run([plantuml_path, "--version"], capture_output=True, check=False)
    logger.debug("PlantUML version: %s", process.stdout.decode().strip())
    return True
