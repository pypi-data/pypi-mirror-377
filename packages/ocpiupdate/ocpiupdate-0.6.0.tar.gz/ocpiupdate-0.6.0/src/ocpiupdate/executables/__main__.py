#!/usr/bin/env python3

"""Script that automatically updates OpenCPI Projects."""

# ruff: noqa: C901

from __future__ import annotations

import argparse
import importlib.metadata
import logging
import sys
import typing
from copy import deepcopy
from pathlib import Path

from lxml import etree

if typing.TYPE_CHECKING:
    from collections.abc import Iterable

from ocpiupdate import ocpi, treesitter
from ocpiupdate.config import ACTIONS, ASSETS, Rename, Translate
from ocpiupdate.version import V2_4_7, Version
from ocpiupdate.xml import PARSER as XML_PARSER
from ocpiupdate.xml import yield_recursive_findall

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ocpiupdate")


class Arguments:
    """Class containing all globally relevant command line arguments."""

    dry_run: bool
    to_version: Version
    verbose: bool

    def __init__(self, namespace: argparse.Namespace) -> None:
        """Construct."""
        self.dry_run = namespace.dry_run
        self.to_version = namespace.to_version
        self.verbose = namespace.verbose


# There are three ways to declare slaves
def yield_slave_workers_from_proxy(path: Path) -> Iterable[str]:
    """
    Yield the names of all of the workers that this worker is a proxy for.

    Yields
    ------
    str
        The next slave worker name from the proxy.

    """
    tree = etree.parse(path, parser=XML_PARSER)
    root = tree.getroot()
    slave = root.attrib.get("slave")
    if slave is not None:
        yield slave.split(".")[-2]
    else:
        slaves = root.find("slaves")
        if slaves is not None:
            for instance in yield_recursive_findall(slaves, "instance"):
                worker = instance.attrib.get("worker")
                if worker is None:
                    logger.error(
                        "File '%s' is malformed: instance without worker. "
                        "File renaming could operate incorrectly",
                        path,
                    )
                else:
                    yield worker.split(".")[-2]
        else:
            slaves = root.findall("slave")
            if slaves is not None:
                for slave in slaves:
                    worker = slave.attrib.get("worker")
                    if worker is not None:
                        yield worker.split(".")[-2]


def v2_4_7_owd_rename(
    worker_directory: Path,
    arguments: Arguments,
    workers_with_proxies: list[str],
) -> bool:
    """
    Rename all OWD files to their v2.4.7 names.

    - Move all *.hdl/*.xml to *.hdl/*-hdl.xml
    - Move all *.rcc/*.xml to *.rcc/*-rcc.xml

    This isn't done for workers that are proxied when moving to v2.4.7 or
    earlier.

    See https://opencpi.dev/t/broken-hdl-worker-search-path-on-slave-attributes/105

    This function ignores OWDs that have already been migrated.
    """
    if arguments.to_version < V2_4_7:
        return False
    name = worker_directory.stem
    model = worker_directory.suffix[1:]
    old_owd_file = worker_directory / f"{name}.xml"
    logger.debug("Checking if '%s' requires a rename", old_owd_file)
    # Ignore already converted workers
    if not old_owd_file.exists():
        logger.debug(
            "File '%s' not found, assuming conversion already completed",
            old_owd_file,
        )
        return False
    # Ignore workers that have a proxy
    if arguments.to_version <= V2_4_7 and worker_directory.stem in workers_with_proxies:
        logger.debug(
            "'%s' is used in a proxy, can't convert in v2.4.7 or earlier",
            old_owd_file,
        )
        return False
    # Rename the file
    new_owd_file = worker_directory / f"{name}-{model}.xml"
    if not arguments.dry_run:
        old_owd_file.rename(new_owd_file)
    logger.info("Moved '%s' to '%s'", old_owd_file, new_owd_file)
    return True


def parse_variables_from_makefiles(
    file_paths: list[Path],
    file_identifier: str,
) -> tuple[bool, dict[str, str]]:
    """Try to parse makefiles, returning a dictionary of their top level variables."""
    variables: dict[str, str] = {}
    node_fragments_to_ignore = ASSETS[file_identifier].treesitter.fragments_to_ignore
    nodes_to_ignore = [
        treesitter.parser.MAKE.parse(fragment.encode("utf-8")).root_node.children[0]
        for fragment in node_fragments_to_ignore
    ]
    node_types_to_ignore = ASSETS[file_identifier].treesitter.types_to_ignore
    for file_path in file_paths:
        if not file_path.exists():
            logger.debug(
                "File '%s' not found, assuming conversion already completed",
                file_path,
            )
            continue
        tree = treesitter.parser.MAKE.parse(file_path.read_bytes())
        for child in tree.root_node.children:
            # If node can be ignored, ignore it
            if child.type in node_types_to_ignore:
                logger.debug(
                    "Node ('%s') of type '%s' on line %d of '%s' is ignored "
                    "due to config",
                    treesitter.node.source_as_str(child),
                    child.type,
                    child.start_point[0],
                    file_path,
                )
                continue
            match_found = False
            for node in nodes_to_ignore:
                if treesitter.node.structural_equality(child, node):
                    logger.debug(
                        "Node ('%s') matches an ignored node",
                        treesitter.node.to_string(child),
                    )
                    match_found = True
                    break
            if match_found:
                continue
            # If variable is parsable, parse it. If not, fail
            if child.type == "variable_assignment":
                try:
                    treesitter.makefile.update_from_variable_assignments(
                        child,
                        variables,
                    )
                    continue
                except RuntimeError as err:
                    logger.warning(
                        "File '%s' not converted: %s",
                        file_path,
                        str(err),
                    )
                    return False, variables
            # Node hasn't been recognised or ignored, so fail
            logger.debug(
                "Node ('%s') of type '%s' not supported when parsing %s to %s in '%s'",
                treesitter.node.source_as_str(child),
                child.type,
                child.start_point,
                child.end_point,
                file_path,
            )
            logger.warning(
                "File '%s' not parsed due to unrecognised node at position %s",
                file_path,
                child.start_point,
            )
            return False, variables
    return True, variables


def check_variables_for_xml(
    variables: dict[str, str],
    file_paths: list[Path],
    file_identifier: str,
) -> bool:
    """Check a collection of variables for validity in a given XML document."""
    accepted_variables = ASSETS[file_identifier].variables.accepted
    not_recommended_variables = ASSETS[file_identifier].variables.not_recommended
    recommended_variables = ASSETS[file_identifier].variables.recommended
    for k in variables:
        if k in accepted_variables:
            continue
        if k in not_recommended_variables:
            logger.warning(
                "Variable '%s' not recommended when converting '%s' (%s)",
                k,
                [str(file_path) for file_path in file_paths],
                not_recommended_variables[k],
            )
            continue
        # Variable not recognised
        logger.warning(
            "Files '%s' not converted due to unrecognised variable: %s",
            [str(file_path) for file_path in file_paths],
            k,
        )
        return False
    for k in recommended_variables:
        if k not in variables:
            logger.warning(
                "Variable '%s' recommended for inclusion when converting '%s' (%s)",
                k,
                [str(file_path) for file_path in file_paths],
                recommended_variables[k],
            )
            continue
    return True


def categorise_by_parent(
    paths: list[Path],
) -> dict[Path, list[Path]]:
    """Categorise a list of paths by their parents."""
    ret: dict[Path, list[Path]] = {}
    for path in paths:
        if path.parent in ret:
            ret[path.parent].append(path)
        else:
            ret[path.parent] = [path]
    return ret


def translate_makefile_to_xml_in_project(  # noqa: PLR0912, PLR0914, PLR0915
    project_directory: Path,
    from_file_identifier: str,
    to_file_identifier: str,
    arguments: Arguments,
) -> bool:
    """Migrate a makefile to an xml file in a project."""
    if arguments.to_version < V2_4_7:
        return False
    logger.debug(
        "translate_makefile_to_xml_in_project(%s, %s, %s)",
        project_directory,
        from_file_identifier,
        to_file_identifier,
    )
    project_relative_old_file_paths = ASSETS[from_file_identifier].paths.makefiles
    old_file_paths = [
        path
        for project_relative_old_file_path in project_relative_old_file_paths
        for path in project_directory.glob(project_relative_old_file_path)
    ]
    old_file_path_groups = categorise_by_parent(old_file_paths)
    any_converted = False
    for old_file_paths in old_file_path_groups.values():
        # Check that all the variables are acceptable, terminate if they aren't
        parsable, variables = parse_variables_from_makefiles(
            old_file_paths,
            from_file_identifier,
        )
        if not parsable:
            continue
        translated_from_makefile_variables = ASSETS[
            to_file_identifier
        ].variables.translations
        xml_variables = {
            translated_from_makefile_variables.get(k, k): v
            for k, v in variables.items()
        }
        valid = check_variables_for_xml(
            xml_variables,
            old_file_paths,
            to_file_identifier,
        )
        if not valid:
            continue
        # Build the XML file
        root_tag = ASSETS[to_file_identifier].tag
        project_relative_new_file_path = ASSETS[from_file_identifier].paths.xml
        assert project_relative_new_file_path is not None  # noqa: S101
        if isinstance(project_relative_new_file_path, str):
            new_file_path = project_directory / project_relative_new_file_path
        else:
            makefile_path = None
            for old_file_path in old_file_paths:
                if old_file_path.stem == "Makefile":
                    makefile_path = old_file_path
                    break
            if makefile_path is None:
                logger.warning(
                    "File '%s' does not define a 'Makefile'",
                    [str(old_file_path) for old_file_path in old_file_paths],
                )
                continue
            new_file_path = project_relative_new_file_path(makefile_path)
        existing_old_file_paths = [
            old_file_path for old_file_path in old_file_paths if old_file_path.exists()
        ]
        if len(existing_old_file_paths) == 0:
            logger.debug(
                "File '%s' not found; assuming nothing to convert",
                [str(old_file_path) for old_file_path in old_file_paths],
            )
            continue
        # Write new files
        if not new_file_path.exists():
            if not arguments.dry_run:
                et_root = etree.Element(root_tag, attrib=xml_variables)
                et_tree = etree.ElementTree(et_root)
                et_tree.write(new_file_path, encoding="utf-8", xml_declaration=True)
            logger.info(
                "Created '%s' from '%s' ('%s', %s)",
                new_file_path,
                [str(old_file_path) for old_file_path in existing_old_file_paths],
                root_tag,
                xml_variables,
            )
        # Modify existing files
        elif len(xml_variables) != 0:
            # Parse the existing XML
            treesitter_tree = treesitter.parser.XML.parse(new_file_path.read_bytes())
            root_node = treesitter_tree.root_node
            old_xml_source = treesitter.node.source_as_bytes(root_node)
            # Ensure no variable collision
            element = treesitter.xml.get_document_element_node_from_document_node(
                root_node,
            )
            if element is None:
                logger.warning(
                    "File '%s' does not contain a root node; aborting",
                    new_file_path,
                )
                continue
            attributes = treesitter.xml.get_attributes_from_document_element_node(
                element,
            )
            for attribute in attributes:
                if attribute in xml_variables:
                    logger.warning(
                        "File '%s' contains variables that are also set in '%s'; "
                        "aborting migration (xml {%s: %s}, makefile {%s: %s})",
                        new_file_path,
                        [
                            str(old_file_path)
                            for old_file_path in existing_old_file_paths
                        ],
                        attribute,
                        attributes[attribute],
                        attribute,
                        xml_variables[attribute],
                    )
                    continue
            # Add the new stuff
            indent = treesitter.xml.get_common_indent_from_document_element_node(
                old_xml_source,
                element,
            )
            new_xml_source = treesitter.xml.add_attributes(
                old_xml_source,
                element,
                xml_variables,
                indent.decode("utf-8") if indent is not None else " ",
            )
            if not arguments.dry_run:
                new_file_path.write_bytes(new_xml_source)
            logger.info(
                "Added content from '%s' to '%s' "
                "(current attributes: %s, added attributes: %s)",
                [str(old_file_path) for old_file_path in existing_old_file_paths],
                new_file_path,
                attributes,
                xml_variables,
            )
            logger.debug(
                "Old content:\n\n%s\nNew content:\n\n%s\n",
                old_xml_source,
                new_xml_source,
            )
        # Delete old files
        for old_file_path in existing_old_file_paths:
            if not arguments.dry_run:
                old_file_path.unlink()
            logger.info("Deleted '%s'", old_file_path)
        any_converted = True
    return any_converted


def main(user_args: list[str] = sys.argv[1:]) -> None:  # noqa: PLR0912, PLR0915
    """Run the script."""
    # Argument parsing
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "projects",
        nargs="*",
        help="The projects to update (defaults to the current directory)",
        type=Path,
    )
    argparser.add_argument(
        "--actions",
        action="store_true",
        help="Print the available actions and quit",
    )
    argparser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what the program would do, but don't write anything to disk",
    )
    argparser.add_argument(
        "--skip-action",
        action="append",
        default=[],
        help="Skip the given action when running the updater",
    )
    argparser.add_argument(
        "--to-version",
        type=Version,
        help="The OpenCPI version to migrate to (2.4.7 [default] or newer)",
        default=V2_4_7,
    )
    argparser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable printing debug messages to stdout",
    )
    argparser.add_argument(
        "--version",
        action="store_true",
        help="Print the version of the program and exit",
    )
    args, unknown_args = argparser.parse_known_args(user_args)
    if len(unknown_args) != 0:
        logger.error("Extra arguments not recognised: %s", unknown_args)
        sys.exit(1)

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.version:
        print(importlib.metadata.version(__package__.split(".")[0]))  # noqa: T201
        sys.exit(0)

    if args.actions:
        for action_name in ACTIONS:
            print(action_name)  # noqa: T201
        sys.exit(0)

    try:  # noqa: PLR1702
        # Start of processing
        if len(args.projects) == 0:
            args.projects = [Path.cwd()]
        arguments = Arguments(args)
        logger.debug("Running over projects '%s' ...", args.projects)
        for project in args.projects:
            if not ocpi.directory_is_a_project(project):
                logger.error("Directory '%s' is not a project", project)
                sys.exit(1)

        # Create project classes
        args.projects = [ocpi.Project(project) for project in args.projects]

        # Get the names of every worker that has a proxy
        workers_with_proxies: list[str] = []
        if arguments.to_version <= V2_4_7:
            for project in args.projects:
                for library in project.yield_libraries():
                    for worker in library.yield_workers():
                        # Ignore everything but RCCs
                        if worker.suffix != ".rcc":
                            continue
                        # Parse its XML
                        if not worker.owd_path.exists():
                            logger.debug(
                                "Worker directory '%s' doesn't have an OWD. "
                                "File renaming could operate incorrectly",
                                worker,
                            )
                            continue
                        workers_with_proxies.extend(
                            yield_slave_workers_from_proxy(worker.owd_path),
                        )
        logger.debug("Workers that are proxied: %s", workers_with_proxies)

        # Do updates
        replace_actions = []
        all_files_moved = []
        for project in args.projects:
            for library in project.yield_libraries():
                for worker in library.yield_workers():
                    v2_4_7_owd_rename(worker, arguments, workers_with_proxies)
            for name, action in ACTIONS.items():
                if name in args.skip_action:
                    continue
                if isinstance(action, Translate):
                    if action.from_format == "makefile" and action.to_format == "xml":
                        translate_makefile_to_xml_in_project(
                            project,
                            action.identifier,
                            action.identifier,
                            arguments,
                        )
                elif isinstance(action, Rename):
                    files_moved = action.run(
                        project,
                        dry_run=arguments.dry_run,
                        logger=logger,
                    )
                    for from_file, to_file in files_moved:
                        replace_actions.extend(
                            action.generate_replace_actions(from_file, to_file),
                        )
                    all_files_moved.extend(files_moved)
                else:
                    logger.warning("Action '%s' isn't supported", name)

        # Fix any links that we've accidentally broken
        logger.debug("Files moved: %s", all_files_moved)
        for orig, broken_link in (
            (orig, dest)
            for orig, dest in all_files_moved
            if dest.is_symlink() and not Path.readlink(dest).exists()
        ):
            logger.debug(
                "Found broken symlink: %s (%s)",
                broken_link,
                broken_link.readlink(),
            )
            try:
                link_target = (
                    (orig.parent / broken_link.readlink()).resolve().absolute()
                )
            except OSError as e:
                logger.warning(
                    "Failed to read link target of '%s': %s",
                    broken_link,
                    e,
                )
                continue
            logger.debug("Broken link target: %s", link_target)

            for original, new in all_files_moved:
                if original == link_target:
                    old_link_target = broken_link.readlink()
                    new_link_target = new.relative_to(
                        broken_link.parent,
                        walk_up=True,
                    )
                    logger.info(
                        "Fixing broken symlink '%s' (was '%s', now '%s')",
                        broken_link,
                        old_link_target,
                        new_link_target,
                    )
                    if not arguments.dry_run:
                        broken_link.unlink()
                        broken_link.symlink_to(new_link_target)
                    break

        # Collect replace actions to reduce the amount of file IO performed
        aggregated_replace_actions = {}
        for action in replace_actions:
            identifier = action.identifier_to_search
            if identifier not in aggregated_replace_actions:
                aggregated_replace_actions[identifier] = deepcopy(action)
            else:
                aggregated_replace_action = aggregated_replace_actions[identifier]
                aggregated_replace_action.text_to_replace.extend(action.text_to_replace)
                aggregated_replace_action.text_to_substitute.extend(
                    action.text_to_substitute,
                )

        # Perform replace actions
        for project in args.projects:
            for action in aggregated_replace_actions.values():
                category = action.identifier_to_search
                if category in {"hdl-worker", "rcc-worker"}:
                    for owd in project.yield_owds(models=[category[:3]]):
                        action.run(owd, dry_run=arguments.dry_run, logger=logger)
                if category == "component":
                    for ocs in project.yield_components():
                        action.run(ocs, dry_run=arguments.dry_run, logger=logger)

    except Exception as err:
        logger.error(str(err))  # noqa: TRY400
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
