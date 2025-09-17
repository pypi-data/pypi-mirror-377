"""Tests for container-style fallback resolution in CLI.

These tests exercise the code paths where `_resolve_dirs` selects
`/designs` and `/output` when neither CLI arguments, environment
variables nor conventional `./designs` folder are present.

We mock `Path.exists`, `Path.is_dir`, and `Path.mkdir` to avoid needing
actual root-level directories while still driving coverage for those
branches (lines previously uncovered in coverage report).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Any

from sys_design_diagram.cli import _resolve_dirs


def test_container_fallback_designs_and_output(monkeypatch, tmp_path):
    """When no -d/-o and no env vars, fallback to /designs and /output if they 'exist'."""
    # Ensure env vars are absent
    monkeypatch.delenv("SDD_DESIGNS_DIR", raising=False)
    monkeypatch.delenv("SDD_OUTPUT_DIR", raising=False)

    # Make sure there is no ./designs conventional directory in cwd
    original_cwd = Path.cwd()
    os.chdir(tmp_path)

    # Keep originals
    orig_exists: Callable[[Path], bool] = Path.exists  # type: ignore[assignment]
    orig_is_dir: Callable[[Path], bool] = Path.is_dir  # type: ignore[assignment]
    orig_mkdir: Any = Path.mkdir

    def fake_exists(self: Path) -> bool:  # type: ignore[override]
        if str(self) in {"/designs", "/output"}:
            return True
        return orig_exists(self)

    def fake_is_dir(self: Path) -> bool:  # type: ignore[override]
        if str(self) in {"/designs", "/output"}:
            return True
        return orig_is_dir(self)

    def fake_mkdir(self: Path, parents: bool = False, exist_ok: bool = False):  # type: ignore[override]
        # Skip actually creating root paths
        if str(self) in {"/designs", "/output"}:
            return None
        return orig_mkdir(self, parents, exist_ok)

    # Apply monkeypatches
    monkeypatch.setattr(Path, "exists", fake_exists)
    monkeypatch.setattr(Path, "is_dir", fake_is_dir)
    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    try:
        designs_dir, output_dir = _resolve_dirs(None, None)
        assert str(designs_dir) == "/designs"
        assert str(output_dir) == "/output"
    finally:
        os.chdir(original_cwd)
