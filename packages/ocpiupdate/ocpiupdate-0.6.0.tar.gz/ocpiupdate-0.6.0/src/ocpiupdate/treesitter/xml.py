"""Functions for handling XML."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tree_sitter

from .error import NodeChildrenLengthError, NodeTypeError
from .node import source_as_str


def get_document_element_node_from_document_node(
    node: tree_sitter.Node,
) -> tree_sitter.Node | None:
    """Get the node with the type `element` that is a child of the root node."""
    for child in node.children:
        if child.type == "element":
            return child
    return None


def get_document_element_tag_node_from_document_element_node(
    node: tree_sitter.Node,
) -> tree_sitter.Node:
    """
    Ensure that the input is a valid XML document primary element.

    Raises
    ------
    NodeChildrenLengthError
        If any node has an incorrect number of children.
    NodeTypeError
        If any node has an incorrect type.

    """
    if len(node.children) not in {1, 2, 3}:
        raise NodeChildrenLengthError(node, ["=1", "=2", "=3"])
    tag_node = node.children[0]
    # <, Name, Attribute[#], >
    # Check that there are at least three children
    if len(tag_node.children) < 3:  # noqa: PLR2004
        raise NodeChildrenLengthError(tag_node, ">=3")
    # Check that the first two children and last one have the correct types
    if tag_node.children[0].type != "<":
        raise NodeTypeError(tag_node.children[0], "<")
    if tag_node.children[1].type != "Name":
        raise NodeTypeError(tag_node.children[1], "Name")
    if tag_node.children[-1].type not in {">", "/>"}:
        raise NodeTypeError(tag_node.children[-1], [">", "/>"])
    return tag_node


def get_attributes_from_document_element_node(node: tree_sitter.Node) -> dict[str, str]:
    """
    Update a variable collection with attributes from an element tree sitter node.

    Raises
    ------
    NodeChildrenLengthError
        If any node has an incorrect number of children.
    NodeTypeError
        If any node has an incorrect type.

    """
    tag_node = get_document_element_tag_node_from_document_element_node(node)
    # Process attribute nodes
    attributes: dict[str, str] = {}
    attribute_nodes = tag_node.children[2:-1]
    for attribute_node in attribute_nodes:
        # Check that node has the right type
        if attribute_node.type != "Attribute":
            raise NodeTypeError(attribute_node, "Attribute")
        # Check that node has the right number of children
        if len(attribute_node.children) != 3:  # noqa: PLR2004
            raise NodeChildrenLengthError(attribute_node, "=3")
        # Check that children have the right types
        if attribute_node.children[0].type != "Name":
            raise NodeTypeError(attribute_node.children[0], "Name")
        name_node = attribute_node.children[0]
        if attribute_node.children[1].type != "=":
            raise NodeTypeError(attribute_node.children[1], "=")
        if attribute_node.children[2].type != "AttValue":
            raise NodeTypeError(attribute_node.children[2], "AttValue")
        # Check that AttValue children are good
        att_value_node = attribute_node.children[2]
        if len(att_value_node.children) != 2:  # noqa: PLR2004
            raise NodeChildrenLengthError(att_value_node, "=2")
        for child in att_value_node.children:
            if child.type not in {'"', "'"}:
                raise NodeTypeError(child, ['"', "'"])
        name = source_as_str(name_node)
        value = source_as_str(att_value_node)[1:-1]
        attributes[name] = value
    return attributes


def get_document_element_node_attributes_from_document_node(
    node: tree_sitter.Node,
) -> dict[str, str] | None:
    """Get the attributes on the top element of an XML document."""
    element = get_document_element_node_from_document_node(node)
    if element is None:
        return None
    return get_attributes_from_document_element_node(element)


def get_common_indent_from_document_element_node(
    source: bytes,
    node: tree_sitter.Node,
) -> bytes | None:
    """Return the common characters used for attribute indentation."""
    tag_node = get_document_element_tag_node_from_document_element_node(node)
    # Find all of the attribute start points and the previous end point
    ends = []
    starts = []
    last_node = tag_node.children[1]
    for attribute in tag_node.children[2:-1]:
        starts.append(attribute.start_byte)
        ends.append(last_node.end_byte)
        last_node = attribute
    indents = [source[end:start] for end, start in zip(ends, starts, strict=True)]
    if len(indents) != 0 and all(x == indents[0] for x in indents):
        return indents[0]
    return None


def add_attributes(
    source: bytes,
    node: tree_sitter.Node,
    attributes: dict[str, str],
    indent: str = " ",
) -> bytes:
    """Add attributes to an element tree sitter node."""
    tag_node = get_document_element_tag_node_from_document_element_node(node)
    last_attribute_node = tag_node.children[-2]
    ret = source[: last_attribute_node.end_byte]
    for k, v in attributes.items():
        ret += f'{indent}{k}="{v}"'.encode()
    ret += source[last_attribute_node.end_byte :]
    return ret
