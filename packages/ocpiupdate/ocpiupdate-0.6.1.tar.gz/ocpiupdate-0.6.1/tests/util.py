"""Collection of things common across tests."""

import contextlib
import os
import pathlib
from collections.abc import Iterator

from ocpiupdate.executables.__main__ import main  # noqa: PLC2701


def ocpiupdate(arguments: str | list[str]) -> None:
    """Run `ocpiupdate` from inside python."""
    if isinstance(arguments, str):
        main(arguments.split())
    else:
        main(arguments)


@contextlib.contextmanager
def cd(x: str | pathlib.Path) -> Iterator[None]:
    """Move to a directory and return when out of scope."""
    d = pathlib.Path.cwd()
    os.chdir(x)
    try:
        yield
    finally:
        os.chdir(d)
