"""Submodule defining common utilities for handling OpenCPI assets."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

import pathlib

from lxml import etree

from . import treesitter
from .xml import PARSER as XML_PARSER

MODELS = ["hdl", "rcc"]


def directory_is_a_library(directory: pathlib.Path) -> bool:
    """Return true if the given directory is a library."""
    # It's a library if
    # - Contains Library.mk
    file_path = directory / "Library.mk"
    if file_path.exists():
        return True
    # - Contains Makefile referencing library.mk
    file_path = directory / "Makefile"
    fragment = b"include $(OCPI_CDK_DIR)/include/library.mk"
    fragment_node = treesitter.parser.MAKE.parse(fragment).root_node.children[0]
    if file_path.exists():
        tree = treesitter.parser.MAKE.parse(file_path.read_bytes())
        for node in tree.root_node.children:
            if treesitter.node.structural_equality(node, fragment_node):
                return True
    # - Contains <name>.xml with tag `library`
    xml_file_path = directory / f"{directory.stem}.xml"
    if xml_file_path.exists():
        et_tree = etree.parse(xml_file_path, parser=XML_PARSER)
        root = et_tree.getroot()
        if root.tag == "library":
            return True
    return False


def directory_is_a_project(directory: pathlib.Path) -> bool:
    """Return True if the given directory is a project."""
    # It's a project if
    # - Contains Project.xml with tag `project`
    xml_file_path = directory / "Project.xml"
    if xml_file_path.exists():
        et_tree = etree.parse(xml_file_path, parser=XML_PARSER)
        root = et_tree.getroot()
        if root.tag == "project":
            return True
    # - Contains Project.mk
    file_path = directory / "Project.mk"
    if file_path.exists():
        return True
    # - Contains Makefile referencing project.mk
    file_path = directory / "Makefile"
    fragment = b"include $(OCPI_CDK_DIR)/include/project.mk"
    fragment_node = treesitter.parser.MAKE.parse(fragment).root_node.children[0]
    if file_path.exists():
        tree = treesitter.parser.MAKE.parse(file_path.read_bytes())
        for node in tree.root_node.children:
            if treesitter.node.structural_equality(node, fragment_node):
                return True
    return False


def yield_specs_from_directory(directory: pathlib.Path) -> Iterable[pathlib.Path]:
    """
    Yield all of the "-spec" files in "specs" within the given directory.

    Yields
    ------
    pathlib.Path
        The next `-spec` file.

    """
    specs = directory / "specs"
    if not specs.exists():
        return
    for path in specs.iterdir():
        if path.suffix != ".xml":
            continue
        if not path.stem.endswith("spec"):
            continue
        yield path


class SpecsOwner(pathlib.Path):
    """Class representing any directory that can contain a "specs" folder."""

    def yield_specs(self) -> Iterable[pathlib.Path]:
        """
        Yield all of the "-spec" files in "specs" within the given directory.

        Yields
        ------
        pathlib.Path
            The next `-spec` file.

        """
        yield from yield_specs_from_directory(self)


class Worker(pathlib.Path):
    """Class packaging functions related to workers."""

    @property
    def owd_path(self) -> pathlib.Path:
        """Get the path to the OWD file from the worker directory path."""
        model = self.suffix[1:]
        owd = self / f"{self.stem}-{model}.xml"
        if not owd.exists():
            owd = self / f"{self.stem}.xml"
        return owd


class Library(SpecsOwner):
    """Class packaging functions related to libraries."""

    def yield_workers(self) -> Iterable[Worker]:
        """
        Yield a generator of worker directory paths from a library path.

        Yields
        ------
        pathlib.Path
            The next worker from the library.

        """
        for path in self.iterdir():
            if not path.is_dir():
                continue
            if len(path.suffixes) == 0:
                continue
            model = path.suffix[1:]
            if model not in MODELS:
                continue
            yield Worker(path)


class Project(SpecsOwner):
    """Class packaging functions related to projects."""

    def yield_components(self) -> Iterable[pathlib.Path]:
        """
        Yield a generator of component file paths.

        Yields
        ------
        pathlib.Path
            The next component from the project.

        """
        # Project level specs
        yield from self.yield_specs()
        # Libraries
        for library in self.yield_libraries():
            # Specs folder
            yield from library.yield_specs()
            # Comp directories
            for path in library.iterdir():
                if not path.is_dir():
                    continue
                if path.suffix != ".comp":
                    continue
                for child in path.iterdir():
                    if child.suffix != ".xml":
                        continue
                    if not child.stem.endswith("comp") and not child.stem.endswith(
                        "spec",
                    ):
                        continue
                    yield child

    def yield_libraries(self) -> Iterable[Library]:
        """
        Yield a generator of library directory paths from a project path.

        Yields
        ------
        pathlib.Path
            The next library from the project.

        """
        components_directory_path = self / "components"
        if components_directory_path.exists():
            if directory_is_a_library(components_directory_path):
                yield Library(components_directory_path)
            else:
                yield from (
                    Library(path)
                    for path in components_directory_path.iterdir()
                    if path.is_dir() and directory_is_a_library(path)
                )
        # hdl/adapters if it exists
        hdl_adapters_path = self / "hdl" / "adapters"
        if hdl_adapters_path.exists():
            yield Library(hdl_adapters_path)
        # hdl/cards if it exists
        hdl_cards_path = self / "hdl" / "cards"
        if hdl_cards_path.exists():
            yield Library(hdl_cards_path)
        # hdl/devices if it exists
        hdl_devices_path = self / "hdl" / "devices"
        if hdl_devices_path.exists():
            yield Library(hdl_devices_path)

    def yield_owds(self, models: list[str] = MODELS) -> Iterable[pathlib.Path]:
        """
        Yield a generator of worker directory paths from a project path.

        Yields
        ------
        pathlib.Path
            The next OWD from the project.

        """
        for path in (Worker(p) for model in models for p in self.rglob(f"*.{model}")):
            if not path.is_dir():
                continue
            if path.owd_path.exists():
                yield path.owd_path
