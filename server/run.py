from server.document import Document, Node

# from pprint import pprint
# from server.embedding import Client
# client = Client()
# pprint(len(client.create('The food was delicious and the waiter...')))

_node_data = [{'element_id': 'A',
               'metadata': {'filename': 'source_file', 'parent_id': None},
               'text': 'Root node',
               'type': 'Node'},
              {'element_id': 'B',
               'metadata': {'filename': 'source_file', 'parent_id': 'A'},
               'text': '1st A Child',
               'type': 'Node'},
              {'element_id': 'D',
               'metadata': {'filename': 'source_file', 'parent_id': 'B'},
               'text': '1st B Child',
               'type': 'Node'},
              {'element_id': 'G',
               'metadata': {'filename': 'source_file', 'parent_id': 'D'},
               'text': '1st D Child',
               'type': 'Node'},
              {'element_id': 'H',
               'metadata': {'filename': 'source_file', 'parent_id': 'G'},
               'text': '1st G Child',
               'type': 'Node'},
              {'element_id': 'E',
               'metadata': {'filename': 'source_file', 'parent_id': 'B'},
               'text': '2nd B Child',
               'type': 'Node'},
              {'element_id': 'I',
               'metadata': {'filename': 'source_file', 'parent_id': 'E'},
               'text': '1st E Child',
               'type': 'Node'},
              {'element_id': 'J',
               'metadata': {'filename': 'source_file', 'parent_id': 'E'},
               'text': '2nd E Child',
               'type': 'Node'},
              {'element_id': 'C',
               'metadata': {'filename': 'source_file', 'parent_id': 'A'},
               'text': '2nd A Child',
               'type': 'Node'},
              {'element_id': 'F',
               'metadata': {'filename': 'source_file', 'parent_id': 'C'},
               'text': '1st C Child',
               'type': 'Node'},
              {'element_id': 'K',
               'metadata': {'filename': 'source_file', 'parent_id': None},
               'text': 'Root node',
               'type': 'Node'},
              {'element_id': 'L',
               'metadata': {'filename': 'source_file', 'parent_id': 'K'},
               'text': '1st K Child',
               'type': 'Node'},
              {'element_id': 'M',
               'metadata': {'filename': 'source_file', 'parent_id': 'L'},
               'text': '1st L Child',
               'type': 'Node'},
              {'element_id': 'O',
               'metadata': {'filename': 'source_file', 'parent_id': 'L'},
               'text': '2nd L Child',
               'type': 'Node'},
              {'element_id': 'N',
               'metadata': {'filename': 'source_file', 'parent_id': 'K'},
               'text': '2nd K Child',
               'type': 'Node'},
              {'element_id': 'P',
               'metadata': {'filename': 'source_file', 'parent_id': 'N'},
               'text': '1st N Child',
               'type': 'Node'},
              ]


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
