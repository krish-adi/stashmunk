from typing import List, Union, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Node:
    id: str = field(default_factory=lambda: str(uuid4()))
    # document id that the node belongs to, when doc_id == node_id then it is the root node
    doc_id: str = None
    # type: text, image, audio, video
    # if anything but text, refer to its multimodal table for embedding
    type: str = 'text'
    # text: content of the node, if multimodal, then it's image description, or audio transcript
    text: str = None
    # metadata: Can hold source specific metadata like source type, URL, author
    metadata: Dict[str, any] = field(default_factory=dict)
    # content exists only when not text
    # content: Any = None # source content, bucket permalink
    parent: str = None
    children: List[str] = field(default_factory=list)
    # properties
    level: int = None  # level away from the root(0) node
    filter: bool = False  # filter flag for the node, if significant or not

    # context properties
    summary: str = None  # summary of the node
    branch_summary: str = None  # full summary of the node and its children

    # embeddings
    text_embedding: any = None  # embedding of node text
    summary_embedding: any = None  # embedding of the node summary
    branch_embedding: any = None  # embedding of the node summary branch
    
    # TODO: Foreign referenced multimodal properties
    # multimodal_embedding could be of different length, so a separate multimodal table
    # directly from the foreign table
    multimodal_embedding: any = None  # embedding of multimodal content
    multimodal_uri: str = None  # uri to the multimodal content, from filestore

    def __str__(self):
        return f"Node( {self.id} -> {self.children} )"

    def __repr__(self):
        return f"Node( {self.id} {self.children} )"
