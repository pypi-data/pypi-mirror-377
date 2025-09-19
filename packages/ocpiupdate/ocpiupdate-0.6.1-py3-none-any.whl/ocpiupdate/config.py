"""Submodule defining the available update operations and lint checks."""

__all__ = [
    "ACTIONS",
    "ASSETS",
    "Rename",
    "Replace",
    "Translate",
]

import dataclasses
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Literal


@dataclasses.dataclass
class Action:
    """TODO."""

    identifier: str


@dataclasses.dataclass
class Replace(Action):
    """TODO."""

    identifier_to_search: str
    text_to_replace: list[str]
    text_to_substitute: list[str]

    def run(
        self,
        path: Path,
        *,
        dry_run: bool = False,
        logger: logging.Logger | None = None,
    ) -> bool:
        """Replace any matching text in a given file."""
        if logger is not None:
            for text_to_replace, text_to_substitute in zip(
                self.text_to_replace,
                self.text_to_substitute,
                strict=True,
            ):
                logger.debug(
                    "replace(%s, %s, %s)",
                    path,
                    text_to_replace,
                    text_to_substitute,
                )
        with path.open("r", encoding="utf-8") as file:
            lines = file.readlines()
        changed_something = False
        for i, line in enumerate(lines):
            for text_to_replace, text_to_substitute in zip(
                self.text_to_replace,
                self.text_to_substitute,
                strict=True,
            ):
                if text_to_replace in line:
                    lines[i] = line.replace(text_to_replace, text_to_substitute)
                    if logger is not None:
                        logger.info(
                            "Replaced '%s' with '%s' on line %d of '%s'",
                            text_to_replace,
                            text_to_substitute,
                            i,
                            path,
                        )
                    changed_something = True
                    break
        if changed_something and not dry_run:
            with path.open("w", encoding="utf-8") as file:
                file.writelines(lines)
        return changed_something


@dataclasses.dataclass
class Rename(Action):
    """TODO."""

    from_glob: str
    to_path: Callable[[Path], Path]
    search_types: list[str]
    search_from: Callable[[Path], list[str]]
    search_to: Callable[[Path], str]

    def run(
        self,
        project: Path,
        *,
        dry_run: bool = False,
        logger: logging.Logger | None = None,
    ) -> list[tuple[Path, Path]]:
        """Rename matching files in the given project."""
        if logger is not None:
            logger.debug(
                "rename(%s, %s, %s)",
                project,
                self.from_glob,
                self.to_path,
            )
        files_moved = []
        for from_file_path in project.glob(self.from_glob):
            to_file_path = self.to_path(from_file_path)
            to_file_path.parent.mkdir(parents=True, exist_ok=True)
            if not dry_run:
                from_file_path.rename(to_file_path)
            if logger is not None:
                logger.info("Moved '%s' to '%s'", from_file_path, to_file_path)
            files_moved.append((from_file_path, to_file_path))
        return files_moved

    def generate_replace_actions(self, from_path: Path, to_path: Path) -> list[Replace]:
        """Generate replace actions relating to this rename action."""
        text_from = self.search_from(from_path)
        text_to = self.search_to(to_path)
        return [
            Replace(
                identifier=self.identifier,
                identifier_to_search=search_type,
                text_to_replace=text_from,
                text_to_substitute=[text_to] * len(text_from),
            )
            for search_type in self.search_types
        ]


@dataclasses.dataclass
class Translate(Action):
    """TODO."""

    from_format: Literal["makefile"] = "makefile"
    to_format: Literal["xml"] = "xml"


ACTIONS = {
    "rename_spec_to_comp_except_project": Rename(
        identifier="component",
        from_glob="components/**/specs/*[-_]spec.xml",
        to_path=lambda file: file.parent.parent
        / f"{file.stem[:-5]}.comp"
        / f"{file.stem[:-5]}-comp.xml",
        search_types=["hdl-worker", "rcc-worker"],
        search_from=lambda file: [file.name, file.stem],
        search_to=lambda file: file.stem[:-5],
    ),
    "rename_protocol_to_prot": Rename(
        identifier="protocol",
        from_glob="**/specs/*[-_]protocol.xml",
        to_path=lambda file: file.parent / f"{file.stem[:-9]}-prot.xml",
        search_types=["component", "hdl-worker", "rcc-worker"],
        search_from=lambda file: [file.name, file.stem],
        search_to=lambda file: file.stem,
    ),
    "rename_underscore_prot_to_hyphen_prot": Rename(
        identifier="protocol",
        from_glob="**/specs/*_prot.xml",
        to_path=lambda file: file.parent / f"{file.stem[:-5]}-prot.xml",
        search_types=["component", "hdl-worker", "rcc-worker"],
        search_from=lambda file: [file.name, file.stem],
        search_to=lambda file: file.stem,
    ),
    "translate_applications_from_makefile_to_xml": Translate(identifier="applications"),
    "translate_hdl_adapters_from_makefile_to_xml": Translate(identifier="hdl-adapters"),
    "translate_hdl_assemblies_from_makefile_to_xml": Translate(
        identifier="hdl-assemblies",
    ),
    "translate_hdl_cards_from_makefile_to_xml": Translate(identifier="hdl-cards"),
    "translate_hdl_device_from_makefile_to_xml": Translate(identifier="hdl-device"),
    "translate_hdl_platforms_from_makefile_to_xml": Translate(
        identifier="hdl-platforms",
    ),
    "translate_hdl_primitives_from_makefile_to_xml": Translate(
        identifier="hdl-primitives",
    ),
    "translate_hdl_worker_from_makefile_to_xml": Translate(identifier="hdl-worker"),
    "translate_project_from_makefile_to_xml": Translate(identifier="project"),
    "translate_rcc_worker_from_makefile_to_xml": Translate(identifier="rcc-worker"),
}


@dataclasses.dataclass
class Paths:
    """TODO."""

    makefiles: list[str] = dataclasses.field(default_factory=list)
    xml: str | Callable[[Path], Path] | None = None


@dataclasses.dataclass
class Treesitter:
    """TODO."""

    fragments_to_ignore: list[str] = dataclasses.field(default_factory=list)
    types_to_ignore: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        """TODO."""
        self.fragments_to_ignore.extend(
            [
                "$(if $(realpath $(OCPI_CDK_DIR)),,\\\n"
                "\t$(error The OCPI_CDK_DIR environment variable is not set correctly.))\n",  # noqa: E501
                "$(if $(OCPI_CDK_DIR),,$(error The OCPI_CDK_DIR environment variable must be set for this Makefile.))\n",  # noqa: E501
            ],
        )
        self.types_to_ignore.extend(["comment"])


@dataclasses.dataclass
class Variables:
    """TODO."""

    accepted: list[str] = dataclasses.field(default_factory=list)
    not_recommended: dict[str, str] = dataclasses.field(default_factory=dict)
    recommended: dict[str, str] = dataclasses.field(default_factory=dict)
    translations: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class Asset:
    """TODO."""

    name: str
    tag: str
    paths: Paths = dataclasses.field(default_factory=Paths)
    treesitter: Treesitter = dataclasses.field(default_factory=Treesitter)
    variables: Variables = dataclasses.field(default_factory=Variables)


_LIBRARY_VARIABLES = Variables(
    accepted=[
        "tests",
        "workers",
    ],
    not_recommended={
        "hdllibraries": (
            "`hdllibraries` imports a list of primitive libraries for "
            "all assets in this component library. This import should "
            "be performed on each worker as necessary not on the "
            "collection as a whole"
        ),
        "package": (
            "`package` directs the asset to pretend it is located "
            "somewhere else. If this is intended, the asset should be "
            "moved to that other location. If its inclusion is "
            "redundant (e.g. the asset is already located in the place "
            "that matches `package`), then `package` should be removed"
        ),
    },
    recommended={},
)


ASSETS = {
    "applications": Asset(
        name="applications",
        paths=Paths(
            makefiles=["applications/Makefile"],
            xml="applications/applications.xml",
        ),
        tag="applications",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/applications.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "applications",
            ],
        ),
    ),
    "hdl-adapters": Asset(
        name="hdl-adapters",
        paths=Paths(
            makefiles=["hdl/adapters/Library.mk", "hdl/adapters/Makefile"],
            xml="hdl/adapters/adapters.xml",
        ),
        tag="library",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/library.mk\n",
            ],
        ),
        variables=_LIBRARY_VARIABLES,
    ),
    "hdl-assemblies": Asset(
        name="hdl-assemblies",
        paths=Paths(
            makefiles=["hdl/assemblies/Makefile"],
            xml="hdl/assemblies/assemblies.xml",
        ),
        tag="assemblies",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/hdl/hdl-assemblies.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "assemblies",
            ],
            not_recommended={
                "componentlibraries": (
                    "`componentlibraries` should be set as a top level "
                    "attribute inside the specific assemblies that the import "
                    "is required for. Setting it at the `assemblies` level is "
                    "not recommended."
                ),
            },
        ),
    ),
    "hdl-cards": Asset(
        name="hdl-cards",
        paths=Paths(
            makefiles=["hdl/cards/Library.mk", "hdl/cards/Makefile"],
            xml="hdl/cards/cards.xml",
        ),
        tag="library",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/library.mk\n",
            ],
        ),
        variables=_LIBRARY_VARIABLES,
    ),
    "hdl-device": Asset(
        name="hdl-device",
        paths=Paths(
            makefiles=[
                "hdl/adapters/*.hdl/Makefile",
                "hdl/cards/*.hdl/Makefile",
                "hdl/devices/*.hdl/Makefile",
            ],
            xml=lambda file: file.parent / f"{file.parent.stem}.xml"
            if (file.parent / f"{file.parent.stem}.xml").exists()
            else file.parent / f"{file.parent.stem}-hdl.xml",
        ),
        tag="hdldevice",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/worker.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "excludeplatforms",
                "excludetargets",
                "hdlexactpart",
                "hdlplatforms",
                "language",
                "libraries",
                "onlyplatforms",
                "onlytargets",
                "sourcefiles",
                "version",
            ],
            recommended={
                "language": (
                    "`language` defaults to 'verilog' if not defined, for "
                    "backwards compatibility with very early versions of "
                    "OpenCPI which didn't feature multiple languages. To avoid "
                    "accidentally creating a Verilog Worker, always define "
                    '`language="vhdl"`'
                ),
                "version": (
                    "`version` defaults to '1' if not defined, for backwards "
                    "compatibility with versions of OpenCPI before ~v1.4. To "
                    "avoid accidentally using the older data flow paradigm, "
                    'always define `version="2"`'
                ),
            },
            translations={"hdllibraries": "libraries"},
        ),
    ),
    "hdl-devices": Asset(
        name="hdl-devices",
        paths=Paths(
            makefiles=["hdl/devices/Library.mk", "hdl/devices/Makefile"],
            xml="hdl/devices/devices.xml",
        ),
        tag="library",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/library.mk\n",
            ],
        ),
        variables=_LIBRARY_VARIABLES,
    ),
    "hdl-platforms": Asset(
        name="hdl-platforms",
        paths=Paths(
            makefiles=["hdl/platforms/Makefile"],
            xml="hdl/platforms/platforms.xml",
        ),
        tag="hdlplatforms",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/hdl/hdl-platforms.mk\n",
            ],
        ),
    ),
    "hdl-primitives": Asset(
        name="hdl-primitives",
        paths=Paths(
            makefiles=["hdl/primitives/Makefile"],
            xml="hdl/primitives/primitives.xml",
        ),
        tag="hdlprimitives",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/hdl/hdl-primitives.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "libraries",
            ],
            recommended={
                "libraries": (
                    "`libraries` is used to determine the order of compilation "
                    "of primitive libraries. If you have any dependencies "
                    "between libraries, you should define it."
                ),
            },
            translations={"primitivelibraries": "libraries"},
        ),
    ),
    "hdl-worker": Asset(
        name="hdl-worker",
        paths=Paths(
            makefiles=[
                "components/*.hdl/Makefile",
                "components/*/*.hdl/Makefile",
            ],
            xml=lambda file: file.parent / f"{file.parent.stem}.xml"
            if (file.parent / f"{file.parent.stem}.xml").exists()
            else file.parent / f"{file.parent.stem}-hdl.xml",
        ),
        tag="hdlworker",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/worker.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "excludeplatforms",
                "excludetargets",
                "hdlexactpart",
                "hdlplatforms",
                "language",
                "libraries",
                "onlyplatforms",
                "onlytargets",
                "sourcefiles",
                "version",
            ],
            recommended={
                "language": (
                    "`language` defaults to 'verilog' if not defined, for "
                    "backwards compatibility with very early versions of "
                    "OpenCPI which didn't feature multiple languages. To avoid "
                    "accidentally creating a Verilog Worker, always define "
                    '`language="vhdl"`'
                ),
                "version": (
                    "`version` defaults to '1' if not defined, for backwards "
                    "compatibility with versions of OpenCPI before ~v1.4. To "
                    "avoid accidentally using the older data flow paradigm, "
                    'always define `version="2"`'
                ),
            },
            translations={"hdllibraries": "libraries"},
        ),
    ),
    "library": Asset(
        name="library",
        paths=Paths(),  # TODO: does this need to be filled in?
        tag="library",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/library.mk\n",
            ],
        ),
        variables=_LIBRARY_VARIABLES,
    ),
    "project": Asset(
        name="project",
        paths=Paths(
            makefiles=["Project.mk", "Makefile"],
            xml="Project.xml",
        ),
        tag="project",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/project.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "packageprefix",
                "packagename",
                "projectdependencies",
            ],
            not_recommended={
                "componentlibraries": (
                    "`componentlibraries` should be specified on the "
                    "particular asset that requires the library to be "
                    "imported, not on collections"
                ),
            },
            recommended={
                "packageprefix": (
                    "`packageprefix` defaults to 'local' if not defined. If "
                    "this is intended, explicitly assign it to 'local'"
                ),
                "packagename": (
                    "`packagename` defaults to the name of the directory this "
                    "file is in if not defined. It should always be defined to "
                    "avoid confusion"
                ),
            },
        ),
    ),
    "rcc-worker": Asset(
        name="rcc-worker",
        paths=Paths(
            makefiles=[
                "components/*.rcc/Makefile",
                "components/*/*.rcc/Makefile",
                "hdl/adapters/*.rcc/Makefile",
                "hdl/cards/*.rcc/Makefile",
                "hdl/devices/*.rcc/Makefile",
            ],
            xml=lambda file: file.parent / f"{file.parent.stem}.xml"
            if (file.parent / f"{file.parent.stem}.xml").exists()
            else file.parent / f"{file.parent.stem}-rcc.xml",
        ),
        tag="rccworker",
        treesitter=Treesitter(
            fragments_to_ignore=[
                "include $(OCPI_CDK_DIR)/include/worker.mk\n",
            ],
        ),
        variables=Variables(
            accepted=[
                "excludeplatforms",
                "excludetargets",
                "includedirs",
                "language",
                "libraries",
                "onlyplatforms",
                "onlytargets",
                "rccplatforms",
                "sourcefiles",
                "staticprereqlibs",
                "version",
            ],
            not_recommended={
                "slave": (
                    "`slave` as a top level attribute is the old syntax from "
                    "before v2.1; this should be changed in favour of using "
                    "`slaves` as a child element"
                ),
                "workers": (
                    "`workers` is used to define multiple workers in one "
                    "worker directory. This is bad practice; they should be "
                    "defined in individual directories"
                ),
            },
            recommended={
                "language": (
                    "`language` defaults to 'C' if not defined, for backwards "
                    "compatibility with very early versions of OpenCPI which "
                    "didn't feature multiple languages. To avoid accidentally "
                    'creating a C Worker, always define `language="c++"`'
                ),
                "version": (
                    "`version` defaults to '1' if not defined, for backwards "
                    "compatibility with versions of OpenCPI before ~v1.4. To "
                    "avoid accidentally using the older data flow paradigm, "
                    'always define `version="2"`'
                ),
            },
            translations={
                "rccincludedirs": "includedirs",
                "rccstaticprereqlibs": "staticprereqlibs",
            },
        ),
    ),
}
