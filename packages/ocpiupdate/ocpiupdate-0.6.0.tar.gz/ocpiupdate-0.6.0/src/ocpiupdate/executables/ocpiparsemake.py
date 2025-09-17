#!/usr/bin/env python3

"""Script that prints out a treesitter parse tree for a makefile."""

from __future__ import annotations

import argparse
import logging
import pathlib
import sys
from typing import TYPE_CHECKING

from ocpiupdate import treesitter

if TYPE_CHECKING:
    import tree_sitter

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ocpiparsemake")


def main() -> None:  # noqa: C901
    """Run the script."""
    # Argument parsing
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "file",
        type=pathlib.Path,
    )
    argparser.add_argument(
        "--no-headings",
        action="store_true",
    )
    argparser.add_argument(
        "--only-variables",
        action="store_true",
    )
    argparser.add_argument(
        "--with-variables",
        action="store_true",
    )
    args, unknown_args = argparser.parse_known_args()
    if len(unknown_args) != 0:
        logger.error("Extra arguments not recognised: %s", unknown_args)
        sys.exit(1)

    makefile_content = pathlib.Path(args.file).read_text(encoding="utf-8")
    tree = treesitter.parser.MAKE.parse(bytes(makefile_content, "utf8"))
    root_node = tree.root_node

    def get_top_level_make_variables(node: tree_sitter.Node) -> dict[str, str]:
        variables: dict[str, str] = {}
        for child in node.children:
            if child.type == "variable_assignment":
                treesitter.makefile.update_from_variable_assignments(child, variables)
        return variables

    if not args.only_variables:
        if not args.no_headings:
            logger.info("##########################")
            logger.info("# Tree-Sitter Parse Tree #")
            logger.info("##########################")
        logger.info(treesitter.node.to_string(root_node))
    if args.only_variables or args.with_variables:
        try:
            variables = get_top_level_make_variables(root_node)
        except RuntimeError as err:
            logger.error("%s of '%s'", str(err), args.file)  # noqa: TRY400
            sys.exit(1)
        if not args.no_headings:
            if not args.only_variables:
                logger.info("")
            logger.info("################################")
            logger.info("# Top Level Makefile Variables #")
            logger.info("################################")
        logger.info("{")
        for i, (k, v) in enumerate(variables.items()):
            logger.info("  '%s': '%s'%s", k, v, "," if i < len(variables) - 1 else "")
        logger.info("}")


if __name__ == "__main__":
    main()
