"""Script to run tests over exemplar projects."""

# ruff: noqa: S101

import difflib
import filecmp
import pathlib
import shutil

import pytest

from .util import ocpiupdate

EXEMPLARS_DIR = pathlib.Path(__file__).parent / "exemplars"
TEMP_DIR = pathlib.Path(__file__).parent / "temp" / "exemplars"
EXEMPLARS_DIRS = [str(p) for p in EXEMPLARS_DIR.iterdir() if p.is_dir()]


def compare_files(file1: pathlib.Path, file2: pathlib.Path) -> str:
    """Return the diff of two files."""
    with pathlib.Path.open(file1, "r") as f1:
        file1_lines = [line.strip() for line in f1.readlines()]
    with pathlib.Path.open(file2, "r") as f2:
        file2_lines = [line.strip() for line in f2.readlines()]
    diff = difflib.unified_diff(
        file1_lines,
        file2_lines,
        fromfile=str(file1),
        tofile=str(file2),
        lineterm="",
    )
    return "\n".join(list(diff))


def compare_directories(dir1: pathlib.Path, dir2: pathlib.Path) -> str:
    """Return the diff of two directories."""
    ret = ""
    comparison = filecmp.dircmp(dir1, dir2)
    for diff_file in comparison.diff_files:
        file1 = dir1 / diff_file
        file2 = dir2 / diff_file
        ret += compare_files(file1, file2)
    for subdir in comparison.common_dirs:
        ret += compare_directories(dir1 / subdir, dir2 / subdir)
    return ret


@pytest.mark.parametrize("exemplar_directory", EXEMPLARS_DIRS)
def test_exemplar(exemplar_directory: str) -> None:
    """Check that an exemplar project produces the `new` from the `old`."""
    exemplar_path = pathlib.Path(exemplar_directory)
    old_project = (exemplar_path / "old").absolute()
    new_project = (exemplar_path / "new").absolute()
    # If the `new` folder doesn't exist, then we are expecting no change
    if not new_project.exists():
        new_project = old_project
    # Copy old project into temporary location to be acted on
    temp_old_project = (TEMP_DIR / exemplar_path.stem).absolute()
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(temp_old_project, ignore_errors=True)
    shutil.copytree(old_project, temp_old_project, symlinks=True)
    # Run ocpiupdate
    ocpiupdate(f"{temp_old_project} --verbose")
    # Diff
    comparison = filecmp.dircmp(temp_old_project, new_project)
    assert len(comparison.left_only) == 0, (
        f"Files only found in updated old project: {comparison.left_only}"
    )
    assert len(comparison.right_only) == 0, (
        f"Files only found in new project: {comparison.right_only}"
    )
    if len(comparison.diff_files) != 0:
        diff = compare_directories(temp_old_project, new_project)
        assert len(diff) == 0, (
            f"Diff failed between {temp_old_project} and {new_project}\n{diff}"
        )
    assert len(comparison.funny_files) == 0, f"Funny files: {comparison.funny_files}"
    # Check that all symlinks are still symlinks, and no new symlinks have been made
    for file in new_project.rglob("*"):
        if not file.is_symlink():
            continue
        temp_old_file = temp_old_project / file.relative_to(new_project)
        assert temp_old_file.is_symlink(), (
            f"{temp_old_file} is not a symlink but {file} is"
        )
        link_target = (temp_old_file.parent / temp_old_file.readlink()).resolve()
        assert link_target.exists(), f"{link_target} does not exist"
    for file in temp_old_project.rglob("*"):
        if not file.is_symlink():
            continue
        new_file = new_project / file.relative_to(temp_old_project)
        assert new_file.is_symlink(), f"{new_file} is a symlink, but {file} isn't"
        link_target = (new_file.parent / new_file.readlink()).resolve()
        assert link_target.exists(), f"{link_target} does not exist"
