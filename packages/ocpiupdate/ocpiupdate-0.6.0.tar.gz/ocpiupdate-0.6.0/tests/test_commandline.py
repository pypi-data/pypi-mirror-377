"""Script to check basic command-line functionality."""

# ruff: noqa: S101

import importlib
import pathlib

import pytest

from .util import cd, ocpiupdate


def test_bad_argument() -> None:
    """Check that extra arguments cause an error."""
    with pytest.raises(SystemExit) as excinfo:
        ocpiupdate("--dry-run --garbo")
    assert excinfo.value.code == 1


def test_version(capfd: pytest.CaptureFixture[str]) -> None:
    """Check that the version is the same as the module."""
    with pytest.raises(SystemExit) as excinfo:
        ocpiupdate("--version")
    captured = capfd.readouterr()
    assert captured.out.strip() == importlib.metadata.version("ocpiupdate")
    assert excinfo.value.code == 0


def test_bad_directory() -> None:
    """Check that the program errors when run on a directory that isn't a project."""
    with pytest.raises(SystemExit) as excinfo:
        ocpiupdate("/tmp --dry-run")  # noqa: S108
    assert excinfo.value.code == 1


def test_bad_current_working_directory() -> None:
    """Check that the program errors when run in a directory that isn't a project."""
    with cd(pathlib.Path(__file__).parent), pytest.raises(SystemExit) as excinfo:
        ocpiupdate("--dry-run")
    assert excinfo.value.code == 1
