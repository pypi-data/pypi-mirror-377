from .quack import NODES as quack_nodes
from .openai_chat import NODES as openai_nodes
from .duckduckgo_research import NODES as ddg_nodes

NODE_FUNCTIONS = {}
NODE_FUNCTIONS.update(quack_nodes)
NODE_FUNCTIONS.update(openai_nodes)
NODE_FUNCTIONS.update(ddg_nodes)

__all__ = ["NODE_FUNCTIONS"]
