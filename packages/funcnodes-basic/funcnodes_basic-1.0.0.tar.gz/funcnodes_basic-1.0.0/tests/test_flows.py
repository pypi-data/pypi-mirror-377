from funcnodes_basic import logic, strings
import pytest_funcnodes
import asyncio


@pytest_funcnodes.nodetest(logic.ForNode)
async def test_if_node_flow1():
    fornode = logic.ForNode()
    endswith = strings.string_endswith()
    ifnode = logic.IfNode()

    fornode.outputs["do"].connect(endswith.inputs["s"])
    endswith.outputs["ends_with"].connect(ifnode.inputs["condition"])
    fornode.outputs["do"].connect(ifnode.inputs["input"])
    ifnode.outputs["on_true"].connect(fornode.inputs["collector"])

    endswith.inputs["suffix"].value = ".txt"
    fornode.inputs["input"].value = ["a.txt", "b.xls", "c.xls", "d.txt", "e.xls"]

    # await fn.run_until_complete(fornode, ifnode, endswith)
    await asyncio.sleep(1.5)
    print("fornode:", fornode.in_trigger)
    print("ifnode:", ifnode.in_trigger)
    print("endswith:", endswith.in_trigger)

    assert fornode.outputs["done"].value == ["a.txt", "d.txt"]
