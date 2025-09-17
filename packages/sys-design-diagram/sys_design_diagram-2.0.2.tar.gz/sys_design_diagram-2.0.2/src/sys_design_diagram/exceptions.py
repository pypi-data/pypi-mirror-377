"""Copyright (c) 2024, Aydin Abdi.

This module defines custom exceptions for the sys-design-diagram package.
"""


class DTFDesignError(Exception):
    """Base exception for the sys-design-diagram package."""


class PlantUMLError(Exception):
    """Base exception for PlantUML-related errors."""


class PlantUMLFileNotFoundError(PlantUMLError):
    """Raised when a PlantUML file is not found."""


class PlantUMLExecutionError(PlantUMLError):
    """Raised when an error occurs during the execution of the PlantUML command."""


class DiagramsError(Exception):
    """Base exception for diagram-related errors."""


class DiagramsFileNotFoundError(DiagramsError):
    """Raised when a diagram file is not found."""


class DiagramsExecutionError(DiagramsError):
    """Raised when an error occurs during the execution of the diagram function."""


class MermaidError(Exception):
    """Base exception for Mermaid-related errors."""


class MermaidFileNotFoundError(MermaidError):
    """Raised when a Mermaid file is not found."""


class MermaidExecutionError(MermaidError):
    """Raised when an error occurs during the execution of the Mermaid command."""
