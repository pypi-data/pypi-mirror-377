import atexit

from jcweaver.core.const import NodeID
from jcweaver.core.nodes.base_node import workflow
from jcweaver.core.nodes.end_node import EndNode
from jcweaver.core.nodes.start_node import StartNode


def save_on_exit():
    startNode = StartNode()
    startNode.id = NodeID.START_ID
    endNode = EndNode()
    endNode.id = NodeID.END_ID

    workflow.save_on_exit()


atexit.register(save_on_exit)
