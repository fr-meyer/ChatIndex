"""
ICTree - Incremental Context Tree for Conversation Management

A hierarchical topic tree for organizing conversation history with automatic
topic detection and node reorganization.
"""

from .ctree import (
    CTree,
    CTreeBuildTimeoutError,
    Node,
    TopicNode,
    MessageNode
)

__version__ = "0.1.1"
__all__ = [
    "CTree",
    "CTreeBuildTimeoutError",
    "Node",
    "TopicNode",
    "MessageNode"
]
