"""Smoke tests that validate the expected project structure.

These checks mirror the repository bootstrap verification command
referenced in the collaboration guide by ensuring directories exist
and the placeholder modules import without raising errors.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRECTORIES = (
    "src",
    "src/protocol",
    "src/auth",
    "src/commit",
    "src/query",
    "src/lineage",
    "src/telemetry",
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "tests/smoke",
)

IMPORTABLE_MODULES = (
    "src",
    "src.protocol",
    "src.auth",
    "src.commit",
    "src.query",
    "src.lineage",
    "src.telemetry",
)


@pytest.mark.parametrize("relative_path", REQUIRED_DIRECTORIES)
def test_required_directories_exist(relative_path: str) -> None:
    """Ensure each expected directory is present in the repository tree."""

    expected_path = REPO_ROOT / relative_path
    assert expected_path.exists(), f"Missing required directory: {relative_path}"
    assert expected_path.is_dir(), f"{relative_path} should be a directory"


@pytest.mark.parametrize("module_name", IMPORTABLE_MODULES)
def test_required_modules_importable(module_name: str) -> None:
    """Import each placeholder package to confirm the namespace resolves."""

    module = importlib.import_module(module_name)
    assert module is not None, f"Failed to import module: {module_name}"
