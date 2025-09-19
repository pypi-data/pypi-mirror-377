"""Functions for handling treesitter parsers."""

import tree_sitter
import tree_sitter_make
import tree_sitter_xml

MAKE = tree_sitter.Parser(tree_sitter.Language(tree_sitter_make.language()))
XML = tree_sitter.Parser(tree_sitter.Language(tree_sitter_xml.language_xml()))
