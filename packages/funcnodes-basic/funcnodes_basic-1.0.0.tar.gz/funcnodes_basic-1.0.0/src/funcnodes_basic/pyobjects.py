"""Utilities that expose common Python object interactions as nodes."""

from __future__ import annotations

from typing import Any, List, Annotated, Dict

import funcnodes_core as fn
from funcnodes_core.io import InputMeta, OutputMeta


def _list_public_attributes(obj: Any) -> List[str]:
    """Return a sorted list of the object's non-private attribute names."""
    if obj is None:
        return []
    try:
        attributes = dir(obj)
    except Exception:  # pragma: no cover - dir() rarely raises but stay defensive
        return []
    # Sorting keeps the dropdown stable for UI components that rely on deterministic
    # value ordering across reruns.
    return sorted(attr for attr in attributes if not attr.startswith("_"))


def _ensure_non_private(attribute: str) -> None:
    """Reject attribute names that appear private."""

    if attribute.startswith("_"):
        raise AttributeError(
            f"Access to private attribute '{attribute}' is not permitted by this node."
        )


@fn.NodeDecorator(
    id="pyobject_get_attribute",
    name="Get Attribute",
    description="Retrieve the value of a non-private attribute from a Python object.",
    # default_io_options=_attribute_io_options(),
)
def get_attribute(
    obj: Annotated[
        Any,
        InputMeta(
            description="Python object that exposes the desired attribute.",
            on={
                "after_set_value": fn.decorator.update_other_io_options(
                    "attribute",
                    _list_public_attributes,
                )
            }
        ),
    ],
    attribute: Annotated[
        str,
        InputMeta(
            description="Name of the attribute to retrieve; private attributes are rejected.",
        ),
    ],
) -> Annotated[
    Any,
    OutputMeta(
        description="Value read from the requested attribute.",
    ),
]:
    """Return the value of the selected non-private attribute for the provided object."""
    _ensure_non_private(attribute)
    if not hasattr(obj, attribute):
        raise AttributeError(
            f"Attribute '{attribute}' is not available on object of type {type(obj).__name__}."
        )
    # getattr performs the actual attribute retrieval once validation is complete.
    return getattr(obj, attribute)


@fn.NodeDecorator(
    id="pyobject_has_attribute",
    name="Has Attribute",
    description="Check whether an object exposes a given attribute.",
)
def has_attribute(
    obj: Annotated[
        Any,
        InputMeta(
            description="Python object that may expose the attribute.",
        ),
    ],
    attribute: Annotated[
        str,
        InputMeta(
            description="Attribute name to probe; private attributes are rejected.",
        ),
    ],
) -> Annotated[
    bool,
    OutputMeta(description="True if the attribute exists on the object."),
]:
    """Return True when the object defines the requested attribute."""

    return hasattr(obj, attribute)


@fn.NodeDecorator(
    id="pyobject_set_attribute",
    name="Set Attribute",
    description="Assign a new value to a non-private attribute on a Python object.",
)
def set_attribute(
    obj: Annotated[
        Any,
        InputMeta(
            description="Python object whose attribute should be updated.",
        ),
    ],
    attribute: Annotated[
        str,
        InputMeta(
            description="Attribute name that will receive the new value.",
        ),
    ],
    value: Annotated[
        Any,
        InputMeta(description="Value to assign to the attribute."),
    ],
) -> Annotated[
    Any,
    OutputMeta(description="The original object after assignment."),
]:
    """Set an attribute on the provided object and return the object for chaining."""

    _ensure_non_private(attribute)
    setattr(obj, attribute, value)
    return obj


@fn.NodeDecorator(
    id="pyobject_delete_attribute",
    name="Delete Attribute",
    description="Remove a non-private attribute from a Python object.",
)
def delete_attribute(
    obj: Annotated[
        Any,
        InputMeta(
            description="Python object whose attribute should be removed.",
            on={
                "after_set_value": fn.decorator.update_other_io_options(
                    "attribute",
                    _list_public_attributes,
                )
            }
        ),
    ],
    attribute: Annotated[
        str,
        InputMeta(
            description="Attribute name to remove from the object.",
        ),
    ],
) -> Annotated[
    Any,
    OutputMeta(description="The original object after deletion."),
]:
    """Delete an attribute from the object and return the mutated object."""

    _ensure_non_private(attribute)
    if not hasattr(obj, attribute):
        raise AttributeError(
            f"Attribute '{attribute}' is not available on object of type {type(obj).__name__}."
        )
    delattr(obj, attribute)
    return obj


NODE_SHELF = fn.Shelf(
    nodes=[
        get_attribute,
        has_attribute,
        set_attribute,
        delete_attribute,
    ],
    name="Python Objects",
    description="Access and transform general Python objects.",
    subshelves=[],
)
