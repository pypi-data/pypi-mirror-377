"""Copyright (c) 2024, Aydin Abdi.

This module contains interfaces for the application.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class DiagramInterface(ABC):
    """Interface for diagram classes."""

    @abstractmethod
    async def create(self, output_path: Path) -> None:
        """Create a diagram and save it to the output path.

        Args:
            output_path: The path to save the diagram.
        """
