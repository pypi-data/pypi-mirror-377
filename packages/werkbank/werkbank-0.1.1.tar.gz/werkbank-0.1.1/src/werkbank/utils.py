"""Entry points discovery for ZnTrack nodes.

This module provides functionality to discover and load all packages
that have registered entry points under 'zntrack.nodes'.
"""

import importlib
import importlib.metadata
import logging
from collections import defaultdict
import inspect
import dataclasses
import typing as t
from zntrack.config import FIELD_TYPE, FieldTypes
import zntrack

log = logging.getLogger(__name__)


def get_registered_nodes(group: str = "zntrack.nodes") -> dict[str, list[str]]:
    """Get all packages that registered into [project.entry-points.'zntrack.nodes']."""
    registered_nodes = defaultdict(list)

    try:
        # Get all entry points for the 'zntrack.nodes' group
        entry_points = importlib.metadata.entry_points(group=group)

        for entry_point in entry_points:
            try:
                # Load the function registered at this entry point
                nodes_func = entry_point.load()

                # Call the function to get the dictionary of module -> node names
                nodes_dict = nodes_func()

                for module_name, node_names in nodes_dict.items():
                    module_name = module_name.replace(
                        "-", "_"
                    )  # Normalize module names
                    registered_nodes[module_name].extend(node_names)

            except Exception as e:
                log.error(f"Failed to load entry point '{entry_point.name}': {e}")
                continue

    except Exception as e:
        log.error(f"Failed to discover entry points: {e}")

    return dict(registered_nodes)


def get_node_info(package: str, node: str) -> dict:
    """Get information about a specific ZnTrack node.

    Parameters
    ----------
    package : str
        The package name, e.g. "ipsuite"
    node : str
        The node class name, e.g. "ASEGeoOpt"
    """
    try:
        module = importlib.import_module(package)
        node_class = getattr(module, node)
    except (ImportError, AttributeError) as e:
        return {"error": str(e)}

    docs = node_class.__doc__ or "No documentation available."
    fields_by_type = defaultdict(dict)
    type_hints = t.get_type_hints(node_class)
    is_node = issubclass(node_class, zntrack.Node)
    deprecated = getattr(node_class, "__deprecated__", False)

    # Collect dataclass field names
    dataclass_field_names = {f.name for f in dataclasses.fields(node_class)}
    for field in dataclasses.fields(node_class):
        field_type = field.metadata.get(FIELD_TYPE)
        hint = type_hints.get(field.name, None)
        if field_type is not None:
            fields_by_type[field_type.value][field.name] = repr(hint)
        if not is_node:
            fields_by_type[FieldTypes.PARAMS.value][field.name] = repr(hint)

    # Collect other members
    methods = {
        "properties": {},
    }

    for attr_name, attr in inspect.getmembers(node_class):
        if attr_name in ["nwd", "state", "uuid"]:
            # we skip default zntrack class attributes
            continue

        if attr_name.startswith("__") or attr_name in dataclass_field_names:
            continue

        # Properties
        if isinstance(attr, property):
            return_type = t.get_type_hints(attr.fget).get("return", None)
            methods["properties"][attr_name] = repr(return_type)

    return {
        "docs": docs,
        "fields": dict(fields_by_type),
        "methods": methods,
        "node": is_node,
        "deprecated": deprecated,
    }


def get_node_code(package: str, node: str) -> str:
    """Get the source code of a specific ZnTrack node.

    Parameters
    ----------
    package : str
        The package name, e.g. "ipsuite"
    node : str
        The node class name, e.g. "ASEGeoOpt"
    """
    try:
        module = importlib.import_module(package)
        node_class = getattr(module, node)
        source_code = inspect.getsource(node_class)
        return source_code
    except (ImportError, AttributeError, TypeError) as e:
        return f"Error retrieving source code: {e}"