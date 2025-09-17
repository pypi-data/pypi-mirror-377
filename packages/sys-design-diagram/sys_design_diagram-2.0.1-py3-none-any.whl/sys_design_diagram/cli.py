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
from typing import Any, Tuple
import os

import click
from sys_design_diagram import __version__ as version
from sys_design_diagram.process_diagrams import ProcessDiagrams, _AsyncProcessor
from sys_design_diagram.log import configure_logging, logger


@click.group()
@click.version_option(version=version, prog_name="System Design Diagram Generator")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Enable verbose mode.")
def cli(**kwargs: Any) -> None:
    """Command line interface for the sys-design-diagram package."""
    verbose = kwargs.get("verbose", False)
    configure_logging(verbose=verbose)
    logger.debug("Verbose mode enabled.")


def _resolve_dirs(designs_dir: Path | None, output_dir: Path | None) -> Tuple[Path, Path]:
    """Resolve designs and output directories using CLI args, env vars, or fallbacks.

    Resolution order:
    1. CLI argument (if provided)
    2. Environment variables SDD_DESIGNS_DIR / SDD_OUTPUT_DIR (if set)
    3. Conventional paths: ./designs (if exists) for designs; ./sys-design-diagram-output for output

    Raises:
        click.BadParameter: If designs directory cannot be determined or does not exist.
    """
    # Constants
    default_output = Path.cwd() / "sys-design-diagram-output"

    # Resolve designs dir
    if designs_dir is None:
        env_designs = os.getenv("SDD_DESIGNS_DIR")
        if env_designs:
            designs_dir = Path(env_designs)
        else:
            # Conventional relative directory ./designs
            conventional = Path.cwd() / "designs"
            if conventional.exists() and conventional.is_dir():
                designs_dir = conventional
            else:
                # Common container mount point
                container_designs = Path("/designs")
                if container_designs.exists() and container_designs.is_dir():
                    designs_dir = container_designs
    if designs_dir is None:
        raise click.BadParameter(
            "Designs directory not provided. Use -d/--designs-dir, set SDD_DESIGNS_DIR, or create a ./designs folder."
        )
    if not designs_dir.exists():
        raise click.BadParameter(f"Designs directory '{designs_dir}' does not exist.")

    # Resolve output dir (dynamic default evaluated at runtime based on cwd)
    if output_dir is None:
        env_output = os.getenv("SDD_OUTPUT_DIR")
        if env_output:
            output_dir = Path(env_output)
        else:
            # Common container mount point for output
            container_output = Path("/output")
            if container_output.exists() and container_output.is_dir():
                output_dir = container_output
    if output_dir is None:
        output_dir = default_output
    output_dir.mkdir(parents=True, exist_ok=True)
    return designs_dir, output_dir


def _run(
    process_fn: _AsyncProcessor,  # type: ignore[arg-type]
    designs_dir: Path | None,
    output_dir: Path | None,
) -> None:
    resolved_designs, resolved_output = _resolve_dirs(designs_dir, output_dir)
    ProcessDiagrams.run(process_fn, resolved_designs, resolved_output)


@cli.command(name="plantuml")
@click.option(
    "-d",
    "--designs-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help="Directory containing design directories (or set SDD_DESIGNS_DIR or create ./designs).",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    show_default=False,
    help="Directory to save generated diagrams (default: ./sys-design-diagram-output, or set SDD_OUTPUT_DIR).",
)
def plantuml(designs_dir: Path | None, output_dir: Path | None) -> None:
    """Generate diagrams from PlantUML files."""
    _run(ProcessDiagrams.process_plantumls, designs_dir, output_dir)


@cli.command(name="diagrams")
@click.option(
    "-d",
    "--designs-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help="Directory containing design directories (or set SDD_DESIGNS_DIR or create ./designs).",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    show_default=False,
    help="Directory to save generated diagrams (default: ./sys-design-diagram-output, or set SDD_OUTPUT_DIR).",
)
def diagrams(designs_dir: Path | None, output_dir: Path | None) -> None:
    """Generate diagrams using the diagrams library."""
    _run(ProcessDiagrams.process_diagrams, designs_dir, output_dir)


@cli.command(name="process-all")
@click.option(
    "-d",
    "--designs-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help="Directory containing design directories (or set SDD_DESIGNS_DIR or create ./designs).",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    show_default=False,
    help="Directory to save generated diagrams (default: ./sys-design-diagram-output, or set SDD_OUTPUT_DIR).",
)
def process_all(designs_dir: Path | None, output_dir: Path | None) -> None:
    """Generate diagrams using PlantUML, diagrams library, and Mermaid."""
    _run(ProcessDiagrams.process_all, designs_dir, output_dir)


@cli.command(name="mermaid")
@click.option(
    "-d",
    "--designs-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help="Directory containing design directories (or set SDD_DESIGNS_DIR or create ./designs).",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    show_default=False,
    help="Directory to save generated diagrams (default: ./sys-design-diagram-output, or set SDD_OUTPUT_DIR).",
)
def mermaid(designs_dir: Path | None, output_dir: Path | None) -> None:
    """Generate diagrams from Mermaid files."""
    _run(ProcessDiagrams.process_mermaids, designs_dir, output_dir)


if __name__ == "__main__":
    cli()
