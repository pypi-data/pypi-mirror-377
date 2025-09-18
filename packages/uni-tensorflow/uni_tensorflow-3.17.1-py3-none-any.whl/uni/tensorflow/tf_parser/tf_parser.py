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
Created on 12/8/22

@author: irenab
"""
from typing import Union, Tuple, List, Dict

from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.multigraph.graph import MultiDiGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.error.defs import UnsupportedOpsError
from uni.common.parsers.base_parser import BaseParser
from .tf_reader import TensorflowReader
from .tf_meta_node import TFMetaNode
from .tf_op_to_factory import tf_op_factory
from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_edge import NnirEdge


class TensorflowParser(BaseParser):

    def __init__(self, model_path, vis_path=None):
        super().__init__(model_path, TensorflowReader, vis_path)
        self.group_first_shared_node_dict: Dict[str, str] = {}

    def verify_supported_nodes(self, meta_graph: MultiDiGraph):
        nodes: List[TFMetaNode] = meta_graph.get_nodes(data=True)
        unsupported_ops = set()
        for node in nodes:
            if node.op not in tf_op_factory:
                unsupported_ops.add(node.tf_op_full_name())
                continue
            elif not tf_op_factory[node.op].is_supported_node(node):
                unsupported_ops.add(tf_op_factory[node.op].tf_op_info(node).op)
                continue
        if unsupported_ops:
            raise UnsupportedOpsError(unsupported_ops)
        return nodes

    @classmethod
    def _convert_meta_node(cls, meta_graph, node) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        assert isinstance(node, TFMetaNode)
        factory = tf_op_factory[node.op]
        # make sure tf validation decorator was set
        assert hasattr(factory.convert, 'valid'), node.op
        return factory.convert(node)

    def _insert_input_variables_from_request(self, request: GraphRequest, nnir_graph: NnirGraph, node: NnirNode,
                                             **kwargs):
        """ this function is to handle layer sharing attribute like kernel and bias in nodes
            that duplicated in building the meta-graph by adding

            logic:
                empty shared_group_id: calling supper
                first member from the group: calling supper and adding to group_first_shared_node_dict
                another member of the group: get first_shared_node_name and clone the "new" edges

        """
        new_inputs = request.const_inputs_to_insert
        if not new_inputs:
            return
        tf_meta_node: TFMetaNode = kwargs["meta_node"]
        assert isinstance(tf_meta_node, TFMetaNode)
        shared_group_id = tf_meta_node.shared_group_id
        if shared_group_id in self.group_first_shared_node_dict:
            assert shared_group_id is not None, "None shared_group_id can't be in the dict"
            first_shared_node_name: str = self.group_first_shared_node_dict[shared_group_id]
            first_shared_node_in_edges: List[NnirEdge] = nnir_graph.get_ordered_in_edges(first_shared_node_name)
            for i, _ in new_inputs.items():
                new_edge = first_shared_node_in_edges[i].clone(dest=node.name)
                nnir_graph.add_edge(edge=new_edge)
            assert len(first_shared_node_in_edges) == len(nnir_graph.get_ordered_in_edges(node.name))
        else:
            super()._insert_input_variables_from_request(request, nnir_graph, node, **kwargs)
            if shared_group_id is not None:
                self.group_first_shared_node_dict[shared_group_id] = node.name
