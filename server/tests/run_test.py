from server.document import Document
from server.document.node import Node
import json

with open('tests/test_node_data.json', 'r') as f:
    _node_data = json.load(f)


def custom_node_factory(obj):
    '''
    {'element_id': 'A',
    'metadata': {'filename': 'source_file', 'parent_id': None},
    'text': 'Root node',
    'type': 'Node'}
    '''
    return Node(
        id=obj['element_id'],
        doc_id=obj['metadata']['filename'],
        text=obj['text'],
        type=obj['type'],
        parent=obj['metadata'].get('parent_id', None),
    )


_doc = Document(node_data=_node_data, node_factory=custom_node_factory)

print(_doc.graph())


def summarize_node(node: Node, document: Document):
    # print(
    #     f'document: {document.id} with node: {node.id} with {len(node.children)} children')
    if len(node.children) == 0:
        node._summary = f"Summary of leaf Node {node.id}: {node.text} summary"
    else:
        node._summary = f"Summary of branch Node {node.id}: {node.text} summary with summaries of children:"
        for child in node.children:
            child_node = document.find_node(child)
            node._summary += f"\n  {child_node.id} - {child_node._summary}"


_doc.traverse_and_apply(summarize_node, direction='leaf')

for _n in _doc._node_list:
    print(f'{_n.id} -> {_n._summary}')
