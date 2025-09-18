# -------------------------------------------------------------------------------
# (c) Copyright 2022 Sony Semiconductor Israel, Ltd. All rights reserved.
#
#      This software, in source or object form (the "Software"), is the
#      property of Sony Semiconductor Israel Ltd. (the "Company") and/or its
#      licensors, which have all right, title and interest therein, You
#      may use the Software only in accordance with the terms of written
#      license agreement between you and the Company (the "License").
#      Except as expressly stated in the License, the Company grants no
#      licenses by implication, estoppel, or otherwise. If you are not
#      aware of or do not agree to the License terms, you may not use,
#      copy or modify the Software. You may use the source code of the
#      Software only for your internal purposes and may not distribute the
#      source code of the Software, any part thereof, or any derivative work
#      thereof, to any third party, except pursuant to the Company's prior
#      written consent.
#      The Software is the confidential information of the Company.
# -------------------------------------------------------------------------------
"""
Created on 8/4/22

@author: irenab
"""
from typing import List, Iterable, Union, Dict, overload, Literal, Iterator, no_type_check, Optional, Generic
from typing import Tuple    # noqa: F401
import itertools
from collections import defaultdict

import networkx as nx

from .typing import NodeObj, NodeKey, NodeObjOrKey, EdgeObj
from .node_graph_api import NodeGraphContext
from uni.common.logger import get_logger

logger = get_logger(__name__)


class MultiDiGraph(Generic[NodeObj, EdgeObj]):
    """ Directed graph with support for multi-edge
    """
    NODE_DATA = 'node'
    EDGE_DATA = 'edge'

    def __init__(self, nodes: Optional[Iterable[NodeObj]] = None, edges: Optional[Iterable[EdgeObj]] = None):
        self.nx_graph = nx.MultiDiGraph()
        nodes = nodes or []
        edges = edges or []
        for n in nodes:
            self.add_node(n)
        for e in edges:
            self.add_edge(e)

    @overload
    def get_nodes(self, data: Literal[True]) -> List[NodeObj]:
        ...    # pragma: no cover

    @overload
    def get_nodes(self, data: Literal[False]) -> List[NodeKey]:
        ...    # pragma: no cover

    def get_nodes(self, data: bool) -> Union[List[NodeKey], List[NodeObj]]:
        """ Get graph nodes
            If data=True, get node objects, otherwise node keys
        """
        index = 1 if data else 0
        # nx returns tuples of (node key, requested attr)
        return [n[index] for n in self.nx_graph.nodes(data=self.NODE_DATA)]

    def get_edges(self) -> List[EdgeObj]:
        """ Get graph edge objects """
        # nx returns tuples of (src, dest, requested attr)
        edges = [e[2] for e in self.nx_graph.edges(data=self.EDGE_DATA)]
        return edges

    def add_node(self, node: NodeObj) -> None:
        if self.node_exists(node.key):
            raise RuntimeError(f'Attempted to add already existing node {node.key}')
        self.nx_graph.add_node(node.key, **{self.NODE_DATA: node})

    def add_edge(self, edge: EdgeObj) -> None:
        if not self.node_exists(edge.src):
            raise RuntimeError(f'Attempted to add edge {edge} for non-existing src node')
        if not self.node_exists(edge.dest):
            raise RuntimeError(f'Attempted to add edge {edge} for non-existing dest node')

        # check if dest already has incoming edge at the specified dest_index
        dest_in_edges: List[EdgeObj] = self.get_ordered_in_edges(edge.dest, check_indices=False)
        if any(e.dest_index == edge.dest_index for e in dest_in_edges):
            raise RuntimeError(f'Attempted to override existing incoming edge {edge.dest_index} of {edge.dest}')

        self.nx_graph.add_edge(edge.src, edge.dest, **{self.EDGE_DATA: edge})

    def add_edges(self, edges: Iterable[EdgeObj]) -> None:
        for e in edges:
            self.add_edge(e)

    def node_exists(self, node_key: NodeKey) -> bool:
        if self._is_node_obj(node_key):
            raise RuntimeError(f'Expected node key, got node object for {node_key.key}')    # type: ignore[union-attr]
        return self.nx_graph.has_node(node_key)

    def get_edge_data(self, src, src_index, dest, dest_index) -> EdgeObj:
        """ Retrieves edge object
            If edge is not found raises RuntimeError """
        edges: List[EdgeObj] = self._unfold_multi_edge(src, dest)
        edges = [e for e in edges if e.src_index == src_index and e.dest_index == dest_index]
        if not edges:
            raise RuntimeError(f'Requested edge data for non-existing edge {src}:{src_index} -> {dest}:{dest_index}')
        assert len(edges) == 1
        return edges[0]

    def edge_exists(self, src, src_index, dest, dest_index) -> bool:
        """ Checks whether an edge exists """
        edges: List[EdgeObj] = self._unfold_multi_edge(src, dest)
        return any(e.src_index == src_index and e.dest_index == dest_index for e in edges)

    @overload
    def topological_sort(self, data: Literal[True]) -> Iterator[NodeObj]:
        ...    # pragma: no cover

    @overload
    def topological_sort(self, data: Literal[False]) -> Iterator[NodeKey]:
        ...    # pragma: no cover

    def topological_sort(self, data: bool) -> Union[Iterator[NodeKey], Iterator[NodeObj]]:
        ts = nx.algorithms.topological_sort(self.nx_graph)
        if data:
            ts = (self.get_node_data(n) for n in ts)
        return ts

    def get_node_data(self, node_key: NodeKey) -> NodeObj:
        if not self.node_exists(node_key):
            raise RuntimeError(f'Requested node data for non-existing node {node_key}')
        return self.nx_graph.nodes[node_key][self.NODE_DATA]

    def get_ordered_in_edges(self, node: NodeObjOrKey, check_indices=True) -> List[EdgeObj]:
        """
        Args:
            node:
            check_indices: if True, makes sure that inputs indices of the edges are sequential
                           (meaning that dest_index of an edge corresponds to edge's index in the returned list)

        Returns:
            A list of node's input edges objects, ordered by input index (dest_index)
        """
        node = self._node_key(node)
        pred = self._get_pred_nodes_keys(node)
        edges_it: Iterator = itertools.chain(*[self._unfold_multi_edge(src, node) for src in pred])
        edges = list(sorted(edges_it, key=lambda e: e.dest_index))
        if check_indices:
            assert all(e.dest_index == i for i, e in enumerate(edges)), node
        return edges

    @overload
    def get_out_edges(self, node: NodeObjOrKey, by_output: Literal[True]) -> Dict[int, List[EdgeObj]]:
        ...

    @overload
    def get_out_edges(self, node: NodeObjOrKey, by_output: Literal[False]) -> List[EdgeObj]:
        ...

    def get_out_edges(self, node: NodeObjOrKey, by_output: bool) -> Union[Dict[int, List[EdgeObj]], List[EdgeObj]]:
        """ Returns node's output edge objects.
            Shared outputs yield multiple EdgeObj objects with same src_index
            If by_output=True, edges are returned as dict with src_index as key
                               and a list of corresponding edges as values
            If by_output=False, edges are returned as flat list """
        next_nodes = self._get_next_nodes_keys(node)
        edges: Iterator = itertools.chain(*[self._unfold_multi_edge(node, dest) for dest in next_nodes])
        if not by_output:
            return list(edges)

        d = defaultdict(list)
        for e in edges:
            d[e.src_index].append(e)
        return dict(d)

    @overload
    def get_ordered_in_nodes(self, node: NodeObjOrKey, data: Literal[True]) -> List[NodeObj]:
        ...

    @overload
    def get_ordered_in_nodes(self, node: NodeObjOrKey, data: Literal[False]) -> List[NodeKey]:
        ...

    def get_ordered_in_nodes(self, node: NodeObjOrKey, data: bool) -> Union[List[NodeObj], List[NodeKey]]:
        """ return list of Node objects in the order of incoming edges.
                If same node is used as two inputs, it will appear twice.
        """
        nodes: List[NodeKey] = [e.src for e in self.get_ordered_in_edges(node)]
        if data:
            nodes: List[NodeObj] = [self.get_node_data(n) for n in nodes]    # type: ignore[no-redef]
        return nodes

    @no_type_check    # TODO
    def get_out_nodes(self, node: NodeObjOrKey, by_output: bool,
                      data: bool) -> Union[List[NodeObjOrKey], Dict[int, NodeObjOrKey]]:
        """ Returns node's output nodes
            data: if True return Node objects, otherwise return node key
            by_output: if True, nodes are returned as dict with output edges src_index as key
                               and a list of corresponding nodes (sharing the output) as values
                       if False, nodes are returned as list with unique nodes
                            so if same node is used as two inputs, it will appear only ones.
                            list is returned instead of set so that the node is not required to be hashable
        """
        out_edges = self.get_out_edges(node, by_output)

        def nodes_from_edges(edges):
            nodes = [e.dest for e in edges]
            if data:
                nodes = [self.get_node_data(n) for n in nodes]
            return nodes

        if by_output:
            # sorting by keys so that it looks nicer
            return {k: nodes_from_edges(v) for k, v in sorted(out_edges.items(), key=lambda t: t[0])}

        res = []
        for r in nodes_from_edges(out_edges):
            if r not in res:
                res.append(r)
        return res

    def node_in_degree(self, node: NodeObjOrKey) -> int:
        """ Node's input degree
            The count is based on actual incoming connections
            """
        return self.nx_graph.in_degree(self._node_key(node))

    def is_source(self, node: NodeObjOrKey) -> bool:
        return self.node_in_degree(node) == 0

    def node_out_degree(self, node: NodeObjOrKey) -> int:
        """ Node's output degree.
            The count is based on actual outgoing edges (i.e. if a node had x output and one of them was removed,
            the output degree will be x-1).
            Shared outgoing edges are counted once.
        """
        return len(self.get_out_edges(node, by_output=True))

    def is_sink(self, node: NodeObjOrKey) -> bool:
        """ Check whether the node is a sink (terminal node, leaf)
            If a node has all outputs detached, is it a sink """
        return self.node_out_degree(node) == 0

    def remove_edge(self, src: NodeKey, src_index: int, dest: NodeKey, dest_index: int) -> None:
        """ Remove edge """
        multi_edge = self.nx_graph.adj[src][dest]

        # find corresponding key in nx multi-edge

        def match(v):
            edge = v[self.EDGE_DATA]
            return edge.src_index == src_index and edge.dest_index == dest_index

        k = [k for k, v in multi_edge.items() if match(v)]
        assert len(k) == 1
        self.nx_graph.remove_edge(src, dest, k[0])

    def remove_edge_by_obj(self, edge: EdgeObj):
        """ remove graph edge containing the 'edge' data object """
        if self.get_edge_data(edge.src, edge.src_index, edge.dest, edge.dest_index) != edge:
            raise ValueError('Mismatch between the provided edge and the actual graph edge data')
        self.remove_edge(edge.src, edge.src_index, edge.dest, edge.dest_index)

    def remove_node(self, node: NodeObjOrKey, reconnect: bool, reindex_input_edges: bool) -> None:
        """ Removes node along with its in and out edges.
            If reconnect=True, prev nodes are connected to next nodes
              Supported only for a node with at most a single input and output.
              Multiple inputs/outputs should be reconnected manually
            If reindex_input_edges=True, input edges dest_index of next nodes are re-indexed
              Example: node A has 3 inputs with dest_index 0, 1, 2.
              Input node in the middle is removed. Now A has two inputs with dest_index 0, 2.
              If a new input is going to replace the removed input right away, there is no need
              to modify the remaining edges. Otherwise, they should be re-indexed to 0, 1
        """
        if reconnect:
            if self.node_in_degree(node) > 1 or self.node_out_degree(node) > 1:
                raise RuntimeError(
                    f'Reconnecting for node with multiple inputs/outputs is ambiguous for node {self._node_key(node)}')
        if reconnect and not self.is_source(node):
            in_edges: List = self.get_ordered_in_edges(node)
            assert len(in_edges) == 1
            in_edge = in_edges[0]
            self.remove_edge(in_edge.src, in_edge.src_index, in_edge.dest, in_edge.dest_index)
            # for now only single output is supported, but it can be shared between several nodes
            for e in self.get_out_edges(node, by_output=False):    # type: EdgeObj
                if e.src_index != 0:
                    raise NotImplementedError()
                self.remove_edge(e.src, e.src_index, e.dest, e.dest_index)
                self.add_edge(e.clone(src=in_edge.src, src_index=in_edge.src_index))

        out_nodes = self.get_out_nodes(node, by_output=False, data=False)
        self._remove_node(node)
        if reindex_input_edges:
            for n in out_nodes:
                self.reindex_in_edges(n)

    def remove_node_if_detached(self, node: NodeObjOrKey):
        """ Remove node if it's disconnected """
        if self.is_source(node) and self.is_sink(node):
            self.remove_node(node, False, False)

    def insert_node_before(self, node: NodeKey, new_node: NodeObj, on_edge_index=None, shape=None):
        """ Insert 'new_node' before 'node' on input_edge.
            If 'node' has a single input, 'on_edge_index' can be omitted.
            If 'node' has multiple inputs, 'on_edge_index' must be specified.
        """
        input_edges = self.get_ordered_in_edges(node)
        if on_edge_index is None:
            if len(input_edges) > 1:
                raise ValueError(f'edge index must be specified for a node with multiple inputs {node}')
            on_edge_index = 0
        edge = input_edges[on_edge_index]
        new_edge1 = edge.clone(dest=new_node.key, dest_index=0)
        new_edge2 = edge.clone(src=new_node.key, src_index=0, shape=shape)
        self.remove_edge_by_obj(edge)
        self.add_node(new_node)
        self.add_edges([new_edge1, new_edge2])

    def get_graph_context_for_node(self, node) -> NodeGraphContext:
        """ Build graph context for a specific node. See NodeGraphContext """
        gself = self

        class Ctx(NodeGraphContext):

            def get_in_nodes(self) -> List[NodeObj]:
                return gself.get_ordered_in_nodes(node, data=True)

            def get_out_nodes(self) -> Dict[int, List[NodeObj]]:
                return gself.get_out_nodes(node, by_output=True, data=True)

            def get_in_degree(self) -> int:
                return gself.node_in_degree(node)

            def get_out_degree(self) -> int:
                return gself.node_out_degree(node)

            def get_in_shapes(self) -> List[tuple]:
                """ Shape is taken from edge's shape attribute.
                    This method is meaningless if shape is not stored """
                in_edges: List = gself.get_ordered_in_edges(node)
                return [e.shape for e in in_edges]

            def get_out_shapes(self) -> List[tuple]:
                """ Shape is taken from edge's shape attribute.
                    This method is meaningless if shape is not stored """
                out_edges: Dict = gself.get_out_edges(node, by_output=True)
                for edges in out_edges.values():
                    assert len(set(e.shape for e in edges)) == 1
                return [edges[0].shape for edges in out_edges.values()]

            def get_in_edges(self) -> List[EdgeObj]:
                return gself.get_ordered_in_edges(node)

            def get_out_edges(self) -> Dict[int, List[EdgeObj]]:
                return gself.get_out_edges(node, by_output=True)

        return Ctx()

    def _remove_node(self, node: NodeObjOrKey):
        self.nx_graph.remove_node(self._node_key(node))

    def _get_pred_nodes_keys(self, node: NodeObjOrKey):
        return self.nx_graph.pred[self._node_key(node)].keys()

    def _get_next_nodes_keys(self, node: NodeObjOrKey):
        return self.nx_graph.adj[self._node_key(node)].keys()

    @staticmethod
    def _is_node_obj(node: NodeObjOrKey) -> bool:
        """ check if node is node object or node key """
        from .typing import is_node_obj
        return is_node_obj(node)

    @classmethod
    def _node_key(cls, node: NodeObjOrKey) -> NodeKey:
        if cls._is_node_obj(node):
            return node.key    # type: ignore  # Item "str" of "Union[Any, Union[str, int]]" has no attribute "key"
        return node

    def _unfold_multi_edge(self, src: NodeObjOrKey, dest: NodeObjOrKey) -> List[EdgeObj]:
        """ Get all edge objects between src and dest nodes
            If nodes are not connected, return empty list """
        src = self._node_key(src)
        dest = self._node_key(dest)
        if src not in self.nx_graph.adj or dest not in self.nx_graph.adj[src]:
            return []

        multi_edge = self.nx_graph.adj[src][dest]
        edges = [me[self.EDGE_DATA] for me in multi_edge.values()]
        return edges

    def reindex_in_edges(self, node: NodeObjOrKey) -> None:
        """ Re-index input edges
            This is needed if some of the input edges are removed completely
        """
        edges: List = self.get_ordered_in_edges(self._node_key(node), check_indices=False)
        if len(edges) != len(set(e.dest_index for e in edges)):
            raise RuntimeError(f'Found more than one input edge with same dest_index {edges}')

        for i, e in enumerate(edges):
            if e.dest_index != i:
                logger.debug(f'Updating dest index to {i} for edge {e}')
                # replacing edge since it's frozen
                self.remove_edge(e.src, e.src_index, e.dest, e.dest_index)
                self.add_edge(e.clone(dest_index=i))

    def validate_graph(self, allow_disconnected_outputs: bool):
        """
        Validates that:
        - graph is connected
        - edges indices are sequential (no gaps)
        - edges data is consistent with graph connectivity
        - shared edges data is identical

        Args:
            allow_disconnected_outputs: if True, output edges indices are not expected to be sequential

        Raises:
            AssertionError
        """
        # weakly = edges orientation doesn't matter
        assert nx.algorithms.components.is_weakly_connected(self.nx_graph)

        def equal_shared_edges(e1, e2):
            return e1.clone(dest='', dest_index=0) == e2.clone(dest='', dest_index=0)

        for node in self.topological_sort(data=False):
            for i, e in enumerate(self.get_ordered_in_edges(node)):    # type: Tuple[int, EdgeObj]
                assert e.dest == node, f'expected dest={node}, actual {e.dest} for input {i} of node {node}'
                assert e.dest_index == i, f'expected dest_index={i}, actual {e.dest_index} for input {i} of node {node}'

            out: Dict[int, List[EdgeObj]] = self.get_out_edges(node, by_output=True)
            if not allow_disconnected_outputs:
                assert sorted(out.keys()) == list(range(len(out))), \
                    f'{node} outgoing edges are not sequential: {sorted(out.keys())} for node {node}'
            for i, edges in out.items():
                assert len(edges) > 0, f'output {i} of {node}'
                assert all(e.src_index == i and e.src == node for e in edges), f'output {i} of {node}'
                assert all(equal_shared_edges(e, edges[0]) for e in edges[1:]), f'output {i} of {node}'
