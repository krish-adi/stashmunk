from server.document.node.base import Node
from server.utils import convert_to_uuid4


def get_nested_dict_value(data_dict, keys_list):
    """
    Retrieves the value from a nested dictionary given a list of keys representing the path.

    Parameters:
    - data_dict (dict): The dictionary to search within.
    - keys_list (list): A list of keys representing the nested path to the desired value.

    Returns:
    - The value found at the nested path if all keys are present; otherwise, None.

    Example:
    >>> data_dict = {
        'user': {
            'name': {
                'first': 'John',
                'last': 'Doe'
            },
            'details': {
                'age': 30,
                'address': {
                    'street': '123 Main St',
                    'city': 'Anytown'
                }
            }
        }
    }
    >>> keys_list = ['user', 'details', 'address', 'city']
    >>> print(get_nested_dict_value(data_dict, keys_list))
    'Anytown'

    >>> keys_list = ['user', 'details', 'email']
    >>> print(get_nested_dict_value(data_dict, keys_list))
    None
    """
    current_level = data_dict
    for key in keys_list:
        if key in current_level:
            current_level = current_level[key]
        else:
            return None
    return current_level


def default_node_factory(node_data: dict, doc_id: str) -> Node:
    _node_values = {k: v for k, v in node_data.items()
                    if k in Node.__annotations__}

    if "doc_id" not in _node_values:
        _node_values["doc_id"] = doc_id

    return Node(**_node_values)


def unstructuredio_node_factory(node_data: dict, doc_id: str) -> Node:
    """
    Creates a Node object for a raw unstructured.io node data.

    Args:
        node_data (dict): The data of the node.
        doc_id (str): The ID of the document that the node is part of.

    Returns:
        Node: The created Node object.

    Example:
    >>> node_data = {'type': 'NarrativeText',
        'element_id': 'aabe02cb8f192fe9b52407b9bdd918fa',
        'metadata': {'coordinates': {'points': [[1097.674560546875,
                304.8235778808594],
                [1097.674560546875, 327.8569030761719],
                [1403.83837890625, 327.8569030761719],
                [1403.83837890625, 304.8235778808594]],
            'system': 'PixelSpace',
            'layout_width': 1512,
            'layout_height': 2063},
            'filename': 'ai_1.pdf',
            'file_directory': 'source',
            'last_modified': '2023-10-03T15:44:44',
            'filetype': 'application/pdf',
            'parent_id': 'e01c80fa1e40a6a4bcf0434a116182c8',
            'page_number': 1,
            'detection_class_prob': 0.7624167799949646},
        'text': 'www.elsevier.com/locate/procedia'}    
    """
    return Node(
        id=convert_to_uuid4(node_data['element_id']),
        doc_id=doc_id,
        type='text',
        text=node_data.get('text', ''),
        parent=get_nested_dict_value(node_data, ['metadata', 'parent_id']),
        metadata={
            'node_type': node_data.get('type', 'Unknown'),
            'node_factory': 'stashmunk.unstructuredio_node_factory',
            'source_info': {
                'page_number': get_nested_dict_value(node_data, ['metadata', 'page_number']),
            },
            'page_layout': {
                'width': get_nested_dict_value(node_data, ['metadata', 'coordinates', 'layout_width']),
                'height': get_nested_dict_value(node_data, ['metadata', 'coordinates', 'layout_height'])
            },
            'element_bbox': {
                'coordinates': get_nested_dict_value(node_data, ['metadata', 'coordinates', 'points']),
                'system': get_nested_dict_value(node_data, ['metadata', 'coordinates', 'system'])
            },
            # 'permalink' :'' # TODO for other sources
        }
    )
