import funcnodes_core as fn
import pytest
import pytest_funcnodes

from funcnodes_basic import pyobjects


class Sample:
    class_attr = "class-level"

    def __init__(self) -> None:
        self.public = "value"
        self._private = "hidden"

    @property
    def public_property(self) -> str:
        return "prop"

    def public_method(self) -> str:
        return "method"


@pytest_funcnodes.nodetest(pyobjects.get_attribute)
async def test_get_attribute_node_exposes_public_attributes():
    node = pyobjects.get_attribute()
    sample = Sample()

    # Setting the object input triggers the attribute dropdown update.
    node.inputs["obj"].value = sample

    options = node.inputs["attribute"].value_options["options"]
    assert options == [
        "class_attr",
        "public",
        "public_method",
        "public_property",
    ]

    node.inputs["attribute"].value = "public"
    await node
    assert node.outputs["out"].value == "value"

    node.inputs["attribute"].value = "public_property"
    await node
    assert node.outputs["out"].value == "prop"

    node.inputs["attribute"].value = "public_method"
    await node
    method = node.outputs["out"].value
    assert callable(method)
    assert method() == "method"

    with pytest.raises(fn.NodeTriggerError):
        node.inputs["attribute"].value = "_private"
        await node

    with pytest.raises(fn.NodeTriggerError):
        node.inputs["attribute"].value = "missing"
        await node


@pytest_funcnodes.nodetest(pyobjects.has_attribute)
async def test_has_attribute_node_checks_presence():
    node = pyobjects.has_attribute()
    sample = Sample()

    node.inputs["obj"].value = sample

    node.inputs["attribute"].value = "public_property"
    await node
    assert node.outputs["out"].value is True

    node.inputs["attribute"].value = "missing"
    await node
    assert node.outputs["out"].value is False

    node.inputs["attribute"].value = "_private"
    await node
    assert node.outputs["out"].value is True


@pytest_funcnodes.nodetest(pyobjects.set_attribute)
async def test_set_attribute_node_updates_value():
    node = pyobjects.set_attribute()
    sample = Sample()

    node.inputs["obj"].value = sample
    node.inputs["attribute"].value = "public"
    node.inputs["value"].value = "updated"
    await node

    assert sample.public == "updated"
    assert node.outputs["out"].value is sample

    node.inputs["attribute"].value = "new_attr"
    node.inputs["value"].value = 42
    await node
    assert getattr(sample, "new_attr") == 42

    with pytest.raises(fn.NodeTriggerError):
        node.inputs["attribute"].value = "_private"
        node.inputs["value"].value = "secret"
        await node


@pytest_funcnodes.nodetest(pyobjects.delete_attribute)
async def test_delete_attribute_node_removes_value():
    node = pyobjects.delete_attribute()
    sample = Sample()

    node.inputs["obj"].value = sample
    node.inputs["attribute"].value = "public"
    await node

    assert not hasattr(sample, "public")
    assert node.outputs["out"].value is sample

    with pytest.raises(fn.NodeTriggerError):
        node.inputs["attribute"].value = "_private"
        await node

    with pytest.raises(fn.NodeTriggerError):
        node.inputs["attribute"].value = "missing"
        await node
