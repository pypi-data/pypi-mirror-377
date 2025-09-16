"""Copyright (c) 2024 Aydin Abdi.

This module provides a command line interface for the sys-design-diagram package.

Usage:
    sys-design-diagram plantuml -d <designs_dir> -o <output_dir>
    sys-design-diagram diagrams -d <designs_dir> -o <output_dir>
    sys-design-diagram mermaid -d <designs_dir> -o <output_dir>
    sys-design-diagram process-all -d <designs_dir> -o <output_dir>

Options:
    -d, --designs-dir <designs_dir>  Directory containing design directories.
    -o, --output-dir <output_dir>    Directory to save generated diagrams.

Commands:
    plantuml    Generate diagrams from PlantUML files.
    diagrams    Generate diagrams using the diagrams library.
    mermaid     Generate diagrams from Mermaid files.
    process-all Generate diagrams using PlantUML, diagrams library, and Mermaid.
"""

from pathlib import Path
from typing import Any

import click
from sys_design_diagram import __version__ as version
from sys_design_diagram.process_diagrams import ProcessDiagrams
from sys_design_diagram.log import configure_logging, logger


@click.group()
@click.version_option(version=version, prog_name="System Design Diagram Generator")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Enable verbose mode.")
def cli(**kwargs: Any) -> None:
    """Command line interface for the sys-design-diagram package."""
    verbose = kwargs.get("verbose", False)
    configure_logging(verbose=verbose)
    logger.debug("Verbose mode enabled.")


@cli.command(name="plantuml")
@click.option(
    "-d",
    "--designs-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory containing design directories.",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "sys-design-diagram-output",
    help="Directory to save generated diagrams.",
)
def plantuml(designs_dir: Path, output_dir: Path) -> None:
    """Generate diagrams from PlantUML files.

    Args:
        designs_dir: Directory containing design directories.
        output_dir: Directory to save generated diagrams.
    """
    ProcessDiagrams.run(ProcessDiagrams.process_plantumls, designs_dir, output_dir)


@cli.command(name="diagrams")
@click.option(
    "-d",
    "--designs-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory containing design directories.",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "sys-design-diagram-output",
    help="Directory to save generated diagrams.",
)
def diagrams(designs_dir: Path, output_dir: Path) -> None:
    """Generate diagrams using the diagrams library.

    Args:
        designs_dir: Directory containing design directories.
        output_dir: Directory to save generated diagrams
    """
    ProcessDiagrams.run(ProcessDiagrams.process_diagrams, designs_dir, output_dir)


@cli.command(name="process-all")
@click.option(
    "-d",
    "--designs-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory containing design directories.",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "sys-design-diagram-output",
    help="Directory to save generated diagrams.",
)
def process_all(designs_dir: Path, output_dir: Path) -> None:
    """Generate diagrams using PlantUML, diagrams library, and Mermaid.

    Args:
        designs_dir: Directory containing design directories.
        output_dir: Directory to save generated diagrams.
    """
    ProcessDiagrams.run(ProcessDiagrams.process_all, designs_dir, output_dir)


@cli.command(name="mermaid")
@click.option(
    "-d",
    "--designs-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory containing design directories.",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "sys-design-diagram-output",
    help="Directory to save generated diagrams.",
)
def mermaid(designs_dir: Path, output_dir: Path) -> None:
    """Generate diagrams from Mermaid files.

    Args:
        designs_dir: Directory containing design directories.
        output_dir: Directory to save generated diagrams.
    """
    ProcessDiagrams.run(ProcessDiagrams.process_mermaids, designs_dir, output_dir)


if __name__ == "__main__":
    cli()
