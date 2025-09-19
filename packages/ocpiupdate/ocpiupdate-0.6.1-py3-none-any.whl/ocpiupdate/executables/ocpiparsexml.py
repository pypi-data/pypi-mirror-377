#!/usr/bin/env python3

"""Script that prints out a treesitter parse tree for an XML file."""

from __future__ import annotations

import argparse
import logging
import pathlib
import sys

from ocpiupdate import treesitter

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("ocpiparsexml")


def main() -> None:
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
        "--only-attributes",
        action="store_true",
    )
    argparser.add_argument(
        "--with-attributes",
        action="store_true",
    )
    args, unknown_args = argparser.parse_known_args()
    if len(unknown_args) != 0:
        logger.error("Extra arguments not recognised: %s", unknown_args)
        sys.exit(1)

    tree = treesitter.parser.XML.parse(pathlib.Path(args.file).read_bytes())
    root_node = tree.root_node
    try:
        element = treesitter.xml.get_document_element_node_from_document_node(root_node)
        attributes = {}
        if element is None:
            logger.error(
                "File '%s' doesn't contain a root element; aborting",
                args.file,
            )
            sys.exit(1)
        else:
            attributes = treesitter.xml.get_attributes_from_document_element_node(
                element,
            )
    except RuntimeError as err:
        logger.error("%s of '%s'", str(err), args.file)  # noqa: TRY400
        sys.exit(1)

    if not args.only_attributes:
        if not args.no_headings:
            logger.info("##########################")
            logger.info("# Tree-Sitter Parse Tree #")
            logger.info("##########################")
        logger.info(treesitter.node.to_string(root_node))
    if args.only_attributes or args.with_attributes:
        if not args.no_headings:
            if not args.only_attributes:
                logger.info("")
            logger.info("############################")
            logger.info("# Top Level XML Attributes #")
            logger.info("############################")
        logger.info("{")
        for i, (k, v) in enumerate(attributes.items()):
            logger.info("  '%s': '%s'%s", k, v, "," if i < len(attributes) - 1 else "")
        logger.info("}")


if __name__ == "__main__":
    main()
