"""Copyright (c) 2024, Aydin Abdi.

This module contains messages for the application.
"""

from enum import Enum


class ErrorMessages(Enum):
    """Error messages for the application."""

    MODULE_NOT_FOUND = "Module {module_name} does not have a component_diagram function."
    MODULE_LOAD_ERROR = "Failed to load module {module_path}: {error}"
    DIAGRAMS_EXECUTION_FAILED = "Failed to execute component_diagram for {module_name}: {error}"
    FILE_NOT_FOUND = "File not found: {file_path}"
    PLANTUML_EXECUTION_FAILED = "Failed to execute PlantUML: {error}"
    MERMAID_EXECUTION_FAILED = "Failed to execute Mermaid: {error}"
    DIRECTORY_NOT_FOUND = "Directory not found: {directory_path}"
    NOT_A_DIRECTORY = "Not a directory: {directory_path}"
    NOT_A_PATH = "Not a path: {path}"
