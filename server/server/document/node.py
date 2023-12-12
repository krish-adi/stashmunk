from typing import List, Union, Dict
from dataclasses import dataclass, field
from uuid import uuid4

ID = Union[int, str, float]


@dataclass
class Node:
    id: ID = field(default_factory=lambda: str(uuid4()))
    text: str = None
    parent: ID = None

    type: str = 'Node'
    # metadata: Can hold source specific metadata like source type, URL, author
    metadata: Dict[str, any] = field(default_factory=dict)

    doc_id: str = None  # document id that the node belongs to
    children: List[ID] = field(default_factory=list)
    _level: int = None  # level away from the root(0) node
    _summary: str = None  # summary of the node
    _summary_branch: any = None  # full summary of the node and its children

    def __str__(self):
        return f"Node( {self.id} -> {self.children} )"

    def __repr__(self):
        return f"Node( {self.id} {self.children} )"
