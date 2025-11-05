"""Smoke tests that validate the expected project structure.

These checks mirror the repository bootstrap verification command
referenced in the collaboration guide by ensuring directories exist,
package markers are present, and the placeholder modules import
without raising errors.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Iterable

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

STRUCTURE_SPEC: tuple[tuple[str, str], ...] = (
    ("src", "src"),
    ("src/protocol", "src.protocol"),
    ("src/auth", "src.auth"),
    ("src/commit", "src.commit"),
    ("src/query", "src.query"),
    ("src/lineage", "src.lineage"),
    ("src/telemetry", "src.telemetry"),
    ("src/storage", "src.storage"),
)

TEST_DIRECTORIES: tuple[str, ...] = (
    "tests",
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "tests/smoke",
)


def _iter_structure_paths() -> Iterable[Path]:
    """Yield the project paths that must exist for the bootstrap check."""

    for relative_path, _ in STRUCTURE_SPEC:
        yield PROJECT_ROOT / relative_path

    for relative_path in TEST_DIRECTORIES:
        yield PROJECT_ROOT / relative_path


@pytest.mark.parametrize(
    "relative_path",
    sorted({path for path in _iter_structure_paths()}, key=lambda candidate: str(candidate)),
    ids=lambda path: str(path.relative_to(PROJECT_ROOT)),
)
def test_required_directories_exist(relative_path: Path) -> None:
    """Ensure each expected directory is present in the repository tree."""

    assert relative_path.exists(), f"Missing required directory: {relative_path}"
    assert relative_path.is_dir(), f"{relative_path} should be a directory"


@pytest.mark.parametrize(
    "package_path",
    [PROJECT_ROOT / path for path, _ in STRUCTURE_SPEC],
    ids=lambda path: str(path.relative_to(PROJECT_ROOT)),
)
def test_package_markers_present(package_path: Path) -> None:
    """Check each package contains an ``__init__`` marker for importability."""

    marker = package_path / "__init__.py"
    assert marker.exists(), f"Missing package marker: {marker}"
    assert marker.is_file(), f"Package marker should be a file: {marker}"


@pytest.mark.parametrize(
    "module_name",
    [module for _, module in STRUCTURE_SPEC],
)
def test_required_modules_importable(module_name: str) -> None:
    """Import each placeholder package to confirm the namespace resolves."""

    module = importlib.import_module(module_name)
    assert module is not None, f"Failed to import module: {module_name}"
