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
from enum import Enum
from typing import List, NamedTuple, Optional, Dict, Generic
from dataclasses import dataclass
import abc

import numpy as np

from uni.common.core.nnir_graph.quant_info import QuantInfoBase
from .typing import NodeObj, EdgeObj


class NodeGraphContext(abc.ABC, Generic[NodeObj, EdgeObj]):
    """ Context provided by graph for a specific node that enables
        the node to query the graph dynamically for info related to that node only """

    @abc.abstractmethod
    def get_in_nodes(self) -> List[NodeObj]:
        pass

    @abc.abstractmethod
    def get_out_nodes(self) -> Dict[int, List[NodeObj]]:
        pass

    @abc.abstractmethod
    def get_in_degree(self) -> int:
        pass

    @abc.abstractmethod
    def get_out_degree(self) -> int:
        pass

    @abc.abstractmethod
    def get_in_shapes(self) -> List[tuple]:
        pass

    @abc.abstractmethod
    def get_out_shapes(self) -> List[tuple]:
        pass

    @abc.abstractmethod
    def get_in_edges(self) -> List[EdgeObj]:
        pass

    @abc.abstractmethod
    def get_out_edges(self) -> Dict[int, List[EdgeObj]]:
        pass


class ConstNodeCfg(NamedTuple):
    name: str
    data: np.ndarray
    quant: Optional[QuantInfoBase] = None


class NodePosition(Enum):
    NODE_BEFORE = 0
    NODE_AFTER = 1


class NodeToInsertCfg(NamedTuple):
    node: NodeObj    # type: ignore
    # for the new edge
    shape: tuple
    node_position: NodePosition
    # add node on a specific input or output edge. Can be omitted for nodes with a single input/output.
    edge_index: Optional[int] = None


# This dict maps between the original dest of an edge we would like to duplicate, to a list of new destinations.
# for example {0: [1, 2]} means that the edge that enters in dest 0 will now be cloned twice and the new edges will have
# dest 1 and 2 respectively.
orig_dest_to_dup_dest_map = Dict[int, List[int]]

NewInputsCfgT = Dict[int, ConstNodeCfg]


@dataclass
class GraphRequest:
    """ Return message from node to notify graph and make requests
        First inputs are detached, then added. For example, for node with 4 inputs,
         inputs_to_detach = [1, 3]
         const_inputs_to_insert = {2: ConstNodeCfg(..)}
         subsequent_node_to_insert = NodeToInsertCfg(node2, shape2)
        will result in original inputs 0, 2 at indices 0, 1,
                       new node at index 2 and
                       new node2 inserted after the node, with shape2 on the edge between them """
    # Node inputs that are not required by the node anymore and should be detached
    # Graph will remove the edges and decide if they input node can be removed altogether
    inputs_to_detach: Optional[List[int]] = None

    # Request new const inputs to be added
    # Dict key is the input index to connect to after inputs were detached and re-indexed
    const_inputs_to_insert: Optional[NewInputsCfgT] = None
    validate_const_insert_at_the_end: bool = True

    # Request additional node to be inserted
    adjacent_node_to_insert: Optional[NodeToInsertCfg] = None

    # Request for duplicating a node and its edges
    dynamic_input_to_duplicate: Optional[orig_dest_to_dup_dest_map] = None

    @staticmethod
    def request_insert_const_as_input(const_name,
                                      data: np.ndarray,
                                      input_index: int,
                                      validate_const_insert_at_the_end=True,
                                      quant: Optional[QuantInfoBase] = None) -> 'GraphRequest':
        """ build request to add const input at input_index """
        const = ConstNodeCfg(const_name, data, quant=quant)
        request = GraphRequest(const_inputs_to_insert={input_index: const},
                               validate_const_insert_at_the_end=validate_const_insert_at_the_end)
        return request
