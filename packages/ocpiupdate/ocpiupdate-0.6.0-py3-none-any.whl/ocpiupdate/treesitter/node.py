"""Functions for handling treesitter nodes."""

import tree_sitter


def to_string(node: tree_sitter.Node, indent: int = 0) -> str:
    """Convert a treesitter parse tree into a printable string."""
    ret = "  " * indent + f"{node.type} [{node.start_point} - {node.end_point}]"
    for child in node.children:
        ret += "\n" + to_string(child, indent + 1)
    return ret


def structural_equality(
    lhs: tree_sitter.Node,
    rhs: tree_sitter.Node,
) -> bool:
    """Check the structural equality of two treesitter parse trees."""
    if lhs.type != rhs.type:
        return False
    if len(lhs.children) != len(rhs.children):
        return False
    if len(lhs.children) == 0:
        return lhs.text == rhs.text
    for lhs_child, rhs_child in zip(lhs.children, rhs.children, strict=True):
        if not structural_equality(lhs_child, rhs_child):
            return False
    return True


def source_as_bytes(node: tree_sitter.Node) -> bytes:
    """Return the `text` of the node, or empty bytes if there is no text."""
    if node.text is None:
        return b""
    return node.text


def source_as_str(node: tree_sitter.Node) -> str:
    """Return the `text` of the node, or the empty string if there is no text."""
    return source_as_bytes(node).decode("utf-8")
