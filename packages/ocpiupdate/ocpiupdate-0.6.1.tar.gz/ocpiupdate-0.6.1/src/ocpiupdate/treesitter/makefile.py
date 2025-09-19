"""Functions for handling makefiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tree_sitter

from .error import NodeChildrenLengthError, NodeTypeError
from .node import source_as_str

ACCEPTED_OPERATOR_TYPES = ["=", ":=", "::=", ":::=", "?=", "+="]


def update_from_variable_assignments(
    node: tree_sitter.Node,
    variables: dict[str, str],
) -> None:
    """
    Update a variable collection with a variable assignment tree sitter node.

    Raises
    ------
    NodeChildrenLengthError
        If any node has an incorrect number of children.
    NodeTypeError
        If any node has an incorrect type.

    """
    # Discount anything we can't parse
    lhs_node = node.children[0]
    op_node = node.children[1]
    rhs_node = None if len(node.children) == 2 else node.children[2]  # noqa: PLR2004
    if lhs_node.type != "word":
        raise NodeTypeError(lhs_node, "word")
    if op_node.type not in ACCEPTED_OPERATOR_TYPES:
        raise NodeTypeError(op_node, ACCEPTED_OPERATOR_TYPES)
    if rhs_node is not None and rhs_node.type != "text":
        raise NodeTypeError(rhs_node, "text")
    if rhs_node is not None and len(rhs_node.children) != 0:
        raise NodeChildrenLengthError(rhs_node, "=0")
    # We can parse
    lhs = source_as_str(lhs_node).lower()
    op = op_node.type
    rhs = "" if rhs_node is None else source_as_str(rhs_node)
    # Catch an error that the treesitter parser has with operator parsing:
    # https://github.com/alemuller/tree-sitter-make/issues/28
    # TODO: change this to a link to an issue on the current dependency
    if lhs.endswith(("+", "?")):
        op = f"{lhs[-1]}{op}"
        lhs = lhs[:-1]
    # Handle rhs containing line continuations and tab characters
    rhs = rhs.replace("\\", " ")
    rhs = rhs.replace("\n", " ")
    rhs = rhs.replace("\t", " ")
    rhs = " ".join(rhs.strip().split())
    # Add to variables
    if op in {"=", ":=", "::=", ":::="} or (op == "?=" and variables.get(lhs)) is None:
        variables[lhs] = rhs
    elif op == "+=":
        current = variables.get(lhs)
        if current is None:
            variables[lhs] = rhs
        else:
            variables[lhs] = f"{variables[lhs]} {rhs}"
