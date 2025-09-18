# -------------------------------------------------------------------------------
# (c) Copyright 2025 Sony Semiconductor Israel, Ltd. All rights reserved.
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
from typing import List

from uni.common.core.multigraph.edge import Edge
from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import (NnirNode, Reshape, InstanceNorm, Add, Mul, Variable, Placeholder,
                                                   GroupNorm)
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase


class InstanceNormSubstitution(NnirSubstituteBase):
    """
    this substitution is for InstanceNormalization to group normalization
    input:  Previous Node -> Reshape (0, num channels, -1) ->
            InstanceNormalization -> Reshape (org shape) -> Mul -> Add
    output: GroupNormalization

    tests are in
        TestInstanceNormOnnx.test_instance_normalization
        TestGroupNormTorch
    """

    substitution_history_msg = 'InstanceNorm -> GroupNorm'

    def get_match_list(self) -> List[List[NnirNode]]:

        def get_num_channels(node: NnirNode, deep_level: int):
            while deep_level > 0:
                if isinstance(node, (Placeholder, Variable)):
                    return None
                node = self.nnir_graph.get_ordered_in_nodes(node, data=True)[0]
                deep_level -= 1
            if not isinstance(node, Reshape):
                return None
            in_shape = self.nnir_graph.get_ordered_in_edges(node, check_indices=True)[0].shape
            return in_shape[1]

        def first_reshape_selector(node: Reshape, graph: NnirGraph):
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                return False
            out_edges = graph.get_out_edges(node, by_output=False)
            if len(out_edges) != 1:
                return False
            target_shape = node.target_shape
            # first reshape should be (0, num_channels, -1)
            if len(target_shape) != 3:
                return False
            if target_shape[0] not in [0, 1]:
                return False
            return True

        def instance_normalization(node: InstanceNorm, graph: NnirGraph):
            in_nodes = graph.get_ordered_in_nodes(node, data=True)
            gamma_node: Variable = in_nodes[1]    # type: ignore
            beta_node: Variable = in_nodes[2]    # type: ignore
            gama_val = gamma_node.data
            beta_val = beta_node.data
            if gama_val.max() != 1 or gama_val.min() != 1:
                return False
            if beta_val.max() != 0 or beta_val.min() != 0:
                return False
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                return False
            out_edges = graph.get_out_edges(node, by_output=False)
            if len(out_edges) != 1:
                return False
            return True

        def second_reshape_selector(node: Reshape, graph: NnirGraph):
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                return False
            out_edges = graph.get_out_edges(node, by_output=False)
            if len(out_edges) != 1:
                return False
            num_channels = get_num_channels(node, 2)
            if num_channels is None:
                return False
            if node.target_shape[1] != num_channels:
                return False
            return True

        def mul_selector(node: Mul, graph: NnirGraph):
            in_nodes = graph.get_ordered_in_nodes(node, data=True)
            if len(in_nodes) != 2:
                return False
            if not in_nodes[1].is_const():
                return False
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                return False
            out_edges = graph.get_out_edges(node, by_output=False)
            if len(out_edges) != 1:
                return False
            const: Variable = in_nodes[1]    # type: ignore
            num_channels = get_num_channels(node, 3)
            if const.data.shape[0] != num_channels:
                return False
            if const.data.size != num_channels:
                return False
            return True

        def add_selector(node: Add, graph: NnirGraph):
            in_nodes = graph.get_ordered_in_nodes(node, data=True)
            if len(in_nodes) != 2:
                return False
            if not in_nodes[1].is_const():
                return False
            const: Variable = in_nodes[1]    # type: ignore
            num_channels = get_num_channels(node, 4)
            if const.data.shape[0] != num_channels:
                return False
            if const.data.size != num_channels:
                return False
            return True

        return self.nodes_linear_op_matcher([
            (Reshape, first_reshape_selector),    # type: ignore
            (InstanceNorm, instance_normalization),    # type: ignore
            (Reshape, second_reshape_selector),    # type: ignore
            (Mul, mul_selector),    # type: ignore
            (Add, add_selector)    # type: ignore
        ])

    def single_match_substitute(self, match: List[NnirNode]):
        assert len(match) == 5
        first_reshape: Reshape = match[0]    # type: ignore
        instance_norm: InstanceNorm = match[1]    # type: ignore
        fake_gama: Variable = self.nnir_graph.get_ordered_in_nodes(instance_norm, data=True)[1]
        fake_beta: Variable = self.nnir_graph.get_ordered_in_nodes(instance_norm, data=True)[2]
        second_reshape: Reshape = match[2]    # type: ignore
        mul: Mul = match[3]    # type: ignore
        add: Add = match[4]    # type: ignore
        mul_const: Variable = self.nnir_graph.get_ordered_in_nodes(mul, data=True)[1]
        add_const: Variable = self.nnir_graph.get_ordered_in_nodes(add, data=True)[1]
        num_groups = first_reshape.target_shape[1]
        num_channels = second_reshape.target_shape[1]
        gamma_node = mul_const.data.reshape((num_channels, ))
        bias_node = add_const.data.reshape((num_channels, ))

        new_node = GroupNorm(name=instance_norm.name, num_groups=num_groups, epsilon=instance_norm.epsilon)
        new_gamma = Variable(name=f"{instance_norm.name}_gamma", data=gamma_node, quant_info=None)
        new_bias = Variable(name=f"{instance_norm.name}_bias", data=bias_node, quant_info=None)
        old_in_edge: Edge = self.nnir_graph.get_ordered_in_edges(first_reshape, check_indices=True)[0]
        old_out_edges = self.nnir_graph.get_out_edges(add, by_output=False)

        for node in [
                first_reshape, instance_norm, second_reshape, mul, add, mul_const, add_const, fake_gama, fake_beta
        ]:
            self.nnir_graph.remove_node(node, reconnect=False, reindex_input_edges=False)

        self.nnir_graph.add_nodes([new_node, new_gamma, new_bias], inject_ctx=True)

        self.nnir_graph.add_edge(old_in_edge.clone(dest=new_node.name))
        for edge in old_out_edges:
            self.nnir_graph.add_edge(edge.clone(src=new_node.name))
        self.nnir_graph.add_edge(Edge(src=new_gamma.name, dest=new_node.name, src_index=0, dest_index=1))
        self.nnir_graph.add_edge(Edge(src=new_bias.name, dest=new_node.name, src_index=0, dest_index=2))
        pass

    def short_name(self):
        return 'InstanceNorm_to_GroupNorm'
