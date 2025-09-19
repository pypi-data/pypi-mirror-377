from dataclasses import dataclass

from jcweaver.core.const import NodeType
from jcweaver.core.nodes.base_node import Node


@dataclass
class StartInputs:
    pass


@dataclass
class StartOutputs:
    pass


class StartNode(Node[StartInputs, StartOutputs]):
    def __init__(self, name="", description="start node"):
        super().__init__(name, NodeType.START, description)
        self.inputs = StartInputs()
        self.outputs = StartOutputs()
