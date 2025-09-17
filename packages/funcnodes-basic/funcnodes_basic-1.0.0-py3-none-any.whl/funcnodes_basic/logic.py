"""Logic Nodes for control flow and decision making."""

from funcnodes_core.node import Node
from typing import Any, List, Optional
from funcnodes_core.io import NodeInput, NodeOutput, NoValue
import asyncio

import funcnodes_core as fn
import time


class IfNode(Node):
    node_id = "if_node"
    node_name = "If"
    on_true = NodeOutput(id="on_true", type=Any)
    on_false = NodeOutput(id="on_false", type=Any)
    condition = NodeInput(id="condition", type=bool)
    input = NodeInput(id="input", type=Any)

    async def func(self, condition: bool, input: Any) -> None:
        if condition:
            self.outputs["on_true"].value = input
        else:
            self.outputs["on_false"].value = input


class WhileNode(Node):
    node_id = "while_node"
    node_name = "While"
    condition = NodeInput(id="condition", type=bool)
    input = NodeInput(id="input", type=Any)
    do = NodeOutput(id="do", type=Any)
    done = NodeOutput(id="done", type=Any)

    async def func(self, condition: bool, input: Any) -> None:
        if self.inputs["condition"].value:
            self.outputs["do"].value = input
            datapaths = [
                ip.datapath
                for ip in self.outputs["do"].connections
                if ip.datapath is not None
            ]

            while datapaths:
                for dp in datapaths:
                    if dp.done(breaking_nodes=[self]):
                        datapaths.remove(dp)
                        break
                else:
                    await asyncio.sleep(0.1)
            self.request_trigger()
        else:
            self.outputs["done"].value = input


class WaitNode(Node):
    node_id = "wait_node"
    node_name = "Wait"
    delay = NodeInput(
        id="delay",
        type=float,
        required=True,
        default=1.0,
        does_trigger=False,
        render_options={"step": "0.1"},
        value_options={"min": 0.0},
    )
    input = NodeInput(id="input", type=Optional[Any])
    output = NodeOutput(id="output", type=Any)

    async def func(self, delay: float, input: Optional[Any] = NoValue) -> None:
        start = time.time()
        remaining_seconds = delay

        if delay > 1:
            with self.progress(desc="Waiting", unit="s", total=delay) as pbar:
                while remaining_seconds > 0:
                    interval = min(remaining_seconds, 1)
                    await asyncio.sleep(interval)
                    now = time.time()
                    elapsed = now - start
                    remaining_seconds = max(0, delay - elapsed)
                    pbar.update(interval)
        else:
            await asyncio.sleep(delay)
        self.outputs["output"].value = input


class ForNode(Node):
    node_id = "for_node"
    node_name = "For"
    input = NodeInput(id="input", type=List[Any])
    do = NodeOutput(id="do", type=Any)
    collector = NodeInput(id="collector", type=Any, does_trigger=False, required=False)
    done = NodeOutput(id="done", type=List[Any])

    async def func(self, input: list, collector: Optional[Any] = None) -> None:
        results = []
        self.outputs["done"].value = NoValue

        iplen = None
        try:
            iplen = len(input)
        except Exception:
            pass

        for i in self.progress(input, desc="Iterating", unit="it", total=iplen):
            self.outputs["do"].set_value(i, does_trigger=True)
            datapaths = [
                ip.datapath
                for ip in self.outputs["do"].connections
                if ip.datapath is not None
            ]

            while datapaths:
                for dp in datapaths:
                    if dp.done(breaking_nodes=[self]):
                        datapaths.remove(dp)
                        break
                else:
                    await asyncio.sleep(0.1)

            v = self.inputs["collector"].value
            if v is not NoValue:
                results.append(v)
                self.inputs["collector"].value = NoValue
        self.outputs["done"].value = results


class CollectorNode(Node):
    node_id = "collector_node"
    node_name = "Collector"

    reset = NodeInput(id="reset", type=Any, does_trigger=True, required=False)
    input = NodeInput(id="input", type=Any)

    output = NodeOutput(id="output", type=List[Any])
    default_reset_inputs_on_trigger = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection = []

    async def func(self, input: Any, reset: Any = NoValue) -> None:
        if reset != NoValue:
            self.collection = []
            self.inputs["reset"].value = NoValue

        self.collection.append(input)
        self.outputs["output"].value = self.collection


NODE_SHELF = fn.Shelf(
    nodes=[IfNode, WhileNode, WaitNode, ForNode, CollectorNode],
    subshelves=[],
    name="Logic",
    description="Control flow and decision making nodes.",
)
