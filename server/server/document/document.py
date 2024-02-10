from typing import List, Union, Callable
from server.document.node import Node
from uuid import uuid4
import asyncio
import inspect
from dataclasses import asdict
import json


def default_node_factory(node: dict, doc_id) -> Node:
    _node_values = {k: v for k, v in node.items() if k in Node.__annotations__}

    if "doc_id" not in _node_values:
        _node_values["doc_id"] = doc_id

    return Node(**_node_values)


class Document:
    def __init__(
        self,
        id: str = None,
        node_list: List[Node] = None,
        node_data: List[dict] = None,
        node_factory: Callable[[dict], Node] = default_node_factory,
        source_type: str = None,
        metadata: dict = {},
    ) -> None:
        if id is not None:
            self.id = id
        else:
            self.id = str(uuid4())

        self.source_type: str = source_type  # source type: pdf, docx, html, url
        # Status of each node, stash-documents-metadata- embedding model, llm model, image model, embed dim, and so on.
        self.metadata: dict = metadata  # source metadata type, url, author, permalink
        self.node_factory: str = node_factory.__name__

        self._node_factory = node_factory

        if node_list is not None:
            self._node_list = node_list
        elif node_data is not None:
            if node_factory is not None:
                _node_list = []
                for _n_d in node_data:
                    _node = node_factory(_n_d, doc_id=self.id)
                    if _node is not None:
                        _node_list.append(_node)
                self._node_list = _node_list
            else:
                self._node_list = [Node(**n) for n in node_data]
        else:
            raise ValueError(
                "Either node_list or node_data must be provided to create a Document"
            )

        # TODO: node dict map index
        self._node_id_map = {node.id: node for node in self._node_list}

        self._set_node_children()
        self._set_node_levels()

        # Node level map
        self._node_level_map = {}
        for node in self._node_list:
            if node.level not in self._node_level_map:
                self._node_level_map[node.level] = []
            self._node_level_map[node.level].append(node)

        self._node_level_max = max(self._node_level_map.keys())

    def to_file(self, filename: str) -> None:
        _node_data_dump = [asdict(_n) for _n in self._node_list]
        _dict = {
            "id": self.id,
            "source_type": self.source_type,
            "metadata": self.metadata,
            # 'node_factory': self.node_factory,
            "node_data": _node_data_dump,
        }

        with open(filename, "w") as _f:
            json.dump(_dict, _f)

        return _dict

    @classmethod
    def from_file(cls, filename: str) -> "Document":
        with open(filename, "r") as _f:
            _dict = json.load(_f)

        return cls(**_dict)

    def find_node(self, node_id) -> Union[Node, None]:
        # TODO: make this into a map dict to eleminate the search of the Node
        # list for children and parent execution
        for node in self._node_list:
            if node.id == node_id:
                return node

        return None

    def find_leaf_nodes(self) -> List[Node]:
        return [node for node in self._node_list if not node.children]

    def find_root_nodes(self) -> List[Node]:
        # Identify the root nodes (the node without parents that is not a child of
        # any other node)
        return [
            node
            for node in self._node_list
            if not any(node.id in n.children for n in self._node_list)
        ]

    def _set_node_children(self):
        # Find parent of a node in a list of nodes and add them to the children list
        for _d in self._node_list:
            if _d.parent is not None:
                for _p in self._node_list:
                    if _p.id == _d.parent:
                        if _d.id not in _p.children:
                            _p.children.append(_d.id)

    def _set_node_levels(self):
        # Create a dictionary to map node ids to node objects
        node_dict = {node.id: node for node in self._node_list}

        root_nodes = self.find_root_nodes()

        # Define a recursive function to set the level of a node and its children
        def set_level(node: Node, level):
            node.level = level
            for child_id in node.children:
                set_level(node_dict[child_id], level + 1)

        # Set the level of the root node and its children
        for root_node in root_nodes:
            set_level(root_node, 0)

    def graph(self, graph_type: str = "mermaid") -> str:
        if graph_type == "mermaid":
            _root_nodes = self.find_root_nodes()
            _graphs = []
            for _root in _root_nodes:
                _graphs.append(self._mermaid_graph(_root))
            _g = (
                "graph TD\n"
                + f"doc_{self.id[:8]} --> "
                + " & ".join([str(r.id) for r in _root_nodes])
                + "\n"
                + "\n".join(_graphs)
            )
            return _g
        else:
            raise ValueError(f"Supported graph types: ['mermaid'], not {graph_type}")

    def _mermaid_graph(self, root: Node) -> str:
        visited = set()
        queue = [root]
        graph = []

        while queue:
            node = queue.pop(0)
            if node.id not in visited:
                visited.add(node.id)
                child_id_list = []
                for child_id in node.children:
                    child_node = next(
                        (n for n in self._node_list if n.id == child_id), None
                    )
                    if child_node is not None:
                        child_id_list.append(str(child_node.id))
                        queue.append(child_node)
                if child_id_list:
                    graph.append(f"{str(node.id)} --> {' & '.join(child_id_list)}")

        return "\n".join(graph)

    def traverse_and_apply(
        self,
        func: Callable[[Node], None],
        direction: str = "root",
        parallel: bool = False,
    ) -> None:

        if parallel:
            if not inspect.iscoroutinefunction(func):
                raise ValueError(
                    "The function must be an `async` coroutine function to use the parallel option."
                )

            async def async_apply_helper(node_list, document, func):
                await asyncio.gather(
                    *(
                        func(**{"node": node, "document": document})
                        for node in node_list
                    )
                )

            if direction == "root":
                _range = range(self._node_level_max + 1)
            elif direction == "leaf":
                _range = range(self._node_level_max, -1, -1)
            else:
                raise ValueError(
                    f"Direction must be either 'root' or 'leaf', not {direction}"
                )

            for _level in _range:
                asyncio.run(
                    async_apply_helper(self._node_level_map[_level], self, func)
                )

        else:
            if direction == "root":
                root_nodes = self.find_root_nodes()

                def traverse_and_apply_helper(
                    document: Document,
                    node: Node,
                    func: Callable[[Node, List[Node]], None],
                ) -> None:
                    func(**{"node": node, "document": document})
                    for child_id in node.children:
                        child_node = document.find_node(child_id)
                        if child_node is not None:
                            traverse_and_apply_helper(document, child_node, func)

                for root in root_nodes:
                    traverse_and_apply_helper(self, root, func)

            elif direction == "leaf":
                leaf_nodes = self.find_leaf_nodes()

                def traverse_and_apply_helper(
                    document: Document,
                    node: Node,
                    func: Callable[[Node, List[Node]], None],
                ) -> None:
                    func(**{"node": node, "document": document})
                    parent_node = document.find_node(node.parent)
                    if parent_node is not None:
                        traverse_and_apply_helper(document, parent_node, func)

                for leaf in leaf_nodes:
                    traverse_and_apply_helper(self, leaf, func)

            else:
                raise ValueError(
                    f"Direction must be either 'root' or 'leaf', not {direction}"
                )

    async def atraverse_and_apply(
        self,
        func: Callable[[Node], None],
        direction: str = "root",
        parallel: bool = False,
    ) -> None:

        if parallel:
            if not inspect.iscoroutinefunction(func):
                raise ValueError(
                    "The function must be an `async` coroutine function to use the parallel option."
                )

            async def async_apply_helper(node_list, document, func):
                await asyncio.gather(
                    *(
                        func(**{"node": node, "document": document})
                        for node in node_list
                    )
                )

            if direction == "root":
                _range = range(self._node_level_max + 1)
            elif direction == "leaf":
                _range = range(self._node_level_max, -1, -1)
            else:
                raise ValueError(
                    f"Direction must be either 'root' or 'leaf', not {direction}"
                )

            for _level in _range:
                await async_apply_helper(self._node_level_map[_level], self, func)

        else:
            if direction == "root":
                root_nodes = self.find_root_nodes()

                async def traverse_and_apply_helper(
                    document: Document,
                    node: Node,
                    func: Callable[[Node, List[Node]], None],
                ) -> None:
                    func(**{"node": node, "document": document})
                    for child_id in node.children:
                        child_node = document.find_node(child_id)
                        if child_node is not None:
                            await traverse_and_apply_helper(document, child_node, func)

                for root in root_nodes:
                    await traverse_and_apply_helper(self, root, func)

            elif direction == "leaf":
                leaf_nodes = self.find_leaf_nodes()

                async def traverse_and_apply_helper(
                    document: Document,
                    node: Node,
                    func: Callable[[Node, List[Node]], None],
                ) -> None:
                    func(**{"node": node, "document": document})
                    parent_node = document.find_node(node.parent)
                    if parent_node is not None:
                        await traverse_and_apply_helper(document, parent_node, func)

                for leaf in leaf_nodes:
                    await traverse_and_apply_helper(self, leaf, func)

            else:
                raise ValueError(
                    f"Direction must be either 'root' or 'leaf', not {direction}"
                )
