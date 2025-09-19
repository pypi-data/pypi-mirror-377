"""Functions for handling treesitter errors."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tree_sitter

from .node import source_as_str


class ParseError(RuntimeError):
    """Subclass of RuntimeError for issues encountered during xml treesitter parses."""

    def __init__(self, node: tree_sitter.Node, message: str) -> None:
        """Construct."""
        message = (
            f"Node ('{source_as_str(node)}') of type '{node.type}' is not supported "
            f"from {node.start_point} to {node.end_point}: {message}"
        )
        super().__init__(message)


class NodeChildrenLengthError(ParseError):
    """Subclass of ParseError for issues with the number of children."""

    def __init__(self, node: tree_sitter.Node, expected: str | list[str]) -> None:
        """Construct."""
        message = f"node has {len(node.children)} children, expected {expected}"
        super().__init__(node, message)


class NodeTypeError(ParseError):
    """Subclass of ParseError for issues with node type."""

    def __init__(self, node: tree_sitter.Node, expected: str | list[str]) -> None:
        """Construct."""
        message = f"node is of '{node.type}', expected '{expected}'"
        super().__init__(node, message)
