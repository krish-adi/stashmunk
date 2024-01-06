from typing import List, Union, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4

ID = Union[int, str, float]


@dataclass
class Node:
    id: ID = field(default_factory=lambda: str(uuid4()))
    doc_id: str = None  # document id that the node belongs to, when doc_id == node_id then it is the root node
    type: str = 'text' # text, image, audio, video
    text: str = None # text content of the node
    # content exists only when not text
    # content: Any = None # source content, bucket permalink
    parent: ID = None    
    
    # metadata: Can hold source specific metadata like source type, URL, author
    metadata: Dict[str, any] = field(default_factory=dict)

    children: List[ID] = field(default_factory=list)
    summary: str = None  # summary of the node    
    branch_summary: str = None  # full summary of the node and its children
    
    # TODO: embeddings
    # content_embedding could be of different length, so a separate multimodal table
    # content_embedding: any = None  # embedding of node content
    text_embedding: any = None # embedding of node text
    summary_embedding: any = None  # embedding of the node summary
    branch_embedding: any = None # embedding of the node summary branch
    
    # properties
    _level: int = None  # level away from the root(0) node    
    _context: dict = field(default_factory=dict)  # context of the node
    _filter: bool = False  # filter flag for the node, if significant or not


    def __str__(self):
        return f"Node( {self.id} -> {self.children} )"

    def __repr__(self):
        return f"Node( {self.id} {self.children} )"
