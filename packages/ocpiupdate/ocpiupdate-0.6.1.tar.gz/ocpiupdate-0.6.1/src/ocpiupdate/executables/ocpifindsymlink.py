#!/usr/bin/env python3

"""Script that prints out all symlinks in a directory tree."""

from __future__ import annotations

import argparse
import logging
import pathlib
import sys
import typing

if typing.TYPE_CHECKING:
    from collections.abc import Iterable

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ocpifindsymlink")


def main() -> None:
    """Run the script."""
    # Argument parsing
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "directory",
        type=pathlib.Path,
    )
    args, unknown_args = argparser.parse_known_args()
    if len(unknown_args) != 0:
        logger.error("Extra arguments not recognised: %s", unknown_args)
        sys.exit(1)

    def yield_all_symlinks(directory: pathlib.Path) -> Iterable[pathlib.Path]:
        """
        Recursively yield all symlinks in a directory.

        Yields
        ------
        pathlib.Path
            The next symlink.

        """
        for path in directory.iterdir():
            if path.is_symlink():
                yield path
            if path.is_dir():
                yield from yield_all_symlinks(path)

    for path in yield_all_symlinks(args.directory):
        logger.info(
            "Link   %s \nTarget %s\n",
            path,
            (path.parent / path.readlink()).resolve().relative_to(pathlib.Path.cwd()),
        )


if __name__ == "__main__":
    main()
