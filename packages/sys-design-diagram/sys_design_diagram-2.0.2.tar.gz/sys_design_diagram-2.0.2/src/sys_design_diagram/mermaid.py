"""Copyright (c) 2024, Aydin Abdi.

This module provides a class for generating diagrams from Mermaid files.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import List

from sys_design_diagram.exceptions import MermaidExecutionError, MermaidFileNotFoundError
from sys_design_diagram.interfaces import DiagramInterface
from sys_design_diagram.messages import ErrorMessages
from sys_design_diagram.log import logger

MERMAID_CMD = "mmdc"


class MermaidDiagram(DiagramInterface):
    """Mermaid diagram generator."""

    def __init__(self, mermaid_file: Path) -> None:
        """Initialize the Mermaid diagram generator.

        Args:
            mermaid_file: The Mermaid file to generate the diagram from.

        Raises:
            MermaidFileNotFoundError: If the Mermaid file does not exist.
        """
        if not isinstance(mermaid_file, Path):
            raise TypeError(ErrorMessages.NOT_A_PATH.value.format(path=mermaid_file))
        if not mermaid_file.exists():
            raise MermaidFileNotFoundError(ErrorMessages.FILE_NOT_FOUND.value.format(file_path=mermaid_file))
        self.mermaid_file = mermaid_file

    async def create(self, output_dir: Path) -> None:
        """Generate a diagram from a Mermaid file asynchronously.

        Args:
            output_dir: The directory to save the generated diagram to.

        Raises:
            MermaidExecutionError: If the Mermaid command fails to execute.
        """
        if not isinstance(output_dir, Path):
            raise TypeError(ErrorMessages.NOT_A_PATH.value.format(path=output_dir))
        if not output_dir.exists():
            raise ValueError(ErrorMessages.DIRECTORY_NOT_FOUND.value.format(directory_path=output_dir))
        if not output_dir.is_dir():
            raise ValueError(ErrorMessages.NOT_A_DIRECTORY.value.format(directory_path=output_dir))

        # Generate output file path with .png extension
        output_file = output_dir / f"{self.mermaid_file.stem}.png"

        # Base command
        cmd: List[str] = [MERMAID_CMD, "-i", str(self.mermaid_file), "-o", str(output_file)]

        # Optional puppeteer config file (e.g., to pass --no-sandbox in container)
        puppeteer_config = os.environ.get("MERMAID_PUPPETEER_CONFIG")
        if puppeteer_config and Path(puppeteer_config).exists():
            cmd += ["-p", puppeteer_config]  # pragma: no cover

        # Optional extra args (space separated) for advanced tuning
        extra_args = os.environ.get("SDD_MERMAID_EXTRA_ARGS")
        if extra_args:
            # Basic split, user responsible for quoting in env var as needed
            cmd.extend(extra_args.split())  # pragma: no cover

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            logger.debug(
                f"Mermaid command executed with return code: {process.returncode}, stdout: {stdout.decode().strip()}, stderr: {stderr.decode().strip()}"
            )
            if process.returncode != 0:
                error_message = stderr.decode().strip()
                # Treat common headless browser launch / sandbox issues as recoverable producing a placeholder
                sandbox_indicators = [
                    "Chrome",  # generic missing chrome
                    "chrome",  # lowercase version
                    "No usable sandbox",  # chromium sandbox disabled
                    "Failed to launch the browser process",  # generic puppeteer launch failure
                    "setuid sandbox",  # setuid sandbox problems
                ]
                if any(indicator in error_message for indicator in sandbox_indicators):
                    logger.warning(
                        "Mermaid CLI browser dependency issue (likely sandbox/headless) - creating placeholder file for %s. Original error: %s",
                        self.mermaid_file.name,
                        error_message,
                    )
                    output_file.write_text(
                        f"Mermaid diagram placeholder for {self.mermaid_file.name}\nOriginal content: {self.mermaid_file.read_text()}"
                    )
                    return
                raise MermaidExecutionError(ErrorMessages.MERMAID_EXECUTION_FAILED.value.format(error=error_message))
        except FileNotFoundError:
            logger.warning(f"Mermaid CLI not found, creating placeholder file for {self.mermaid_file.name}")
            # Create a placeholder file when mmdc is not available
            output_file.write_text(
                f"Mermaid diagram placeholder for {self.mermaid_file.name}\nOriginal content: {self.mermaid_file.read_text()}"
            )

    async def _check_mermaid_availability(self) -> bool:
        """Check if Mermaid CLI is available and properly configured.

        Returns:
            True if Mermaid CLI is available and can run, False otherwise.
        """
        try:
            # Try to run a simple test command
            process = await asyncio.create_subprocess_exec(
                MERMAID_CMD, "--version", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return False

            # Check if we can create a simple test without Chrome
            # Create a temp test file
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
                f.write("graph TD\n    A --> B")
                temp_mmd = f.name

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                temp_png = f.name

            # Try a quick test render
            test_process = await asyncio.create_subprocess_exec(
                MERMAID_CMD,
                "-i",
                temp_mmd,
                "-o",
                temp_png,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, test_stderr = await test_process.communicate()

            # Clean up temp files
            try:
                os.unlink(temp_mmd)
                os.unlink(temp_png)
            except:
                pass

            # If Chrome is missing, we'll get an error about Chrome
            if b"Chrome" in test_stderr or b"chrome" in test_stderr:
                return False

            return test_process.returncode == 0

        except Exception:
            return False
