# -------------------------------------------------------------------------------
# (c) Copyright 2024 Sony Semiconductor Israel, Ltd. All rights reserved.
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
Created on 9/25/24

@author: lotanw
"""
from typing import List, Sequence

from uni.common.core.nnir_graph.nnir_edge import NnirEdge
from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Sqrt, Mul, ReduceSum, Variable, Abs
from uni.common.core.nnir_graph.nnir_nodes.norm import Norm
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase
from uni.common.core.node_history import NodeHistory


class NormSubstitution(NnirSubstituteBase):
    """
    this substitution is for norm when mul + reduce_sum + sqrt to norm is found
    input:  mul + reduce_sum + sqrt
    output: norm
    """

    substitution_history_msg = 'Mul + Reduce_sum + Sqrt -> Frobenius Norm'

    def get_match_list(self) -> List[List[NnirNode]]:

        def abs_selector(node: NnirNode, graph: NnirGraph):
            if node.get_quant(0) is not None:
                # making sure no quantization after abs
                return False
            in_nodes = graph.get_ordered_in_nodes(node, data=True)
            if len(in_nodes) != 1:
                return False
            # must be 1 output node Mul and 2 output edges, Mul should represent Pow.
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                return False
            out_edges = graph.get_out_edges(node, by_output=False)
            if len(out_edges) != 2 or out_edges[0].dest != out_nodes[0] or out_edges[1].dest != out_nodes[0]:
                return False
            return True

        def mul_selector(node: NnirNode, graph: NnirGraph):
            if node.get_quant(0) is not None:
                # making sure no quantization after mul
                return False
            in_nodes = graph.get_ordered_in_nodes(node, data=True)
            if len(in_nodes) != 2 or in_nodes[0] != in_nodes[1]:
                # must be two inputs, must be the same input. This Mul should represent Pow
                return False
            if isinstance(in_nodes[0], Variable) or isinstance(in_nodes[1], Variable):
                # making sure no variable input
                return False
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                return False
            return True

        def reduce_sum_selector(node: NnirNode, graph: NnirGraph):
            if node.get_quant(0) is not None:
                # making sure no quantization after reduce_sum
                return False
            in_nodes = graph.get_ordered_in_nodes(node, data=True)
            if len(in_nodes) != 1:
                return False
            if len(node.axes) not in [1, 2]:    # type: ignore
                # allowing only 1 axis for ord == 2 or 2 axes for ord == 'fro'
                return False
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                return False
            return True

        def sqrt_selector(node: NnirNode, graph: NnirGraph):
            in_nodes = graph.get_ordered_in_nodes(node, data=True)
            if len(in_nodes) != 1:
                return False
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                return False
            out_edges = graph.get_out_edges(node, by_output=False)
            if len(out_edges) != 1:
                return False
            return True

        abs_norm_substitution = self.nodes_linear_op_matcher([(Abs, abs_selector), (Mul, mul_selector),
                                                              (ReduceSum, reduce_sum_selector), (Sqrt, sqrt_selector)])
        all_norm_substitutions = self.nodes_linear_op_matcher([(Mul, mul_selector), (ReduceSum, reduce_sum_selector),
                                                               (Sqrt, sqrt_selector)])
        assert len(all_norm_substitutions) >= len(abs_norm_substitution)
        # mul in abs_norm_substitutions is the second node
        abs_norm_mul_names = set([e[1].name for e in abs_norm_substitution])
        # mul in regular norm_substitutions is the first node
        none_abs_substitutions = [e for e in all_norm_substitutions if e[0].name not in abs_norm_mul_names]
        return abs_norm_substitution + none_abs_substitutions

    def single_match_substitute(self, match: List[NnirNode]):
        abs_node = None
        if len(match) == 3:
            mul, redsum, sqrt = match
        elif len(match) == 4:
            abs_node, mul, redsum, sqrt = match
        else:
            raise ValueError(f"norm substitution matched unexpected number of values: {match}")
        node_name = mul.name
        node_op_info = mul.op_info()
        desc = self.substitution_history_msg
        if abs_node is not None:
            node_name = abs_node.name
            node_op_info = abs_node.op_info()
            desc = f"Abs + {desc}"
        node_history = NodeHistory(node_op_info, desc=desc)
        axes = redsum.axes if isinstance(redsum.axes, List) else list(redsum.axes)    # type: ignore
        ord_val = 2 if len(axes) == 1 else 'fro'

        if abs_node is not None:
            # using abs in edges for the new graph
            in_edges = self.nnir_graph.get_ordered_in_edges(abs_node)
            assert len(in_edges) == 1
        else:
            # using mul in edges for the new graph
            in_edges = self.nnir_graph.get_ordered_in_edges(mul)
            assert len(in_edges) == 2
            # in case input node is mul, should represent pow with two inputs
            assert in_edges[0].src == in_edges[1].src

        out_edges: Sequence[NnirEdge] = self.nnir_graph.get_out_edges(sqrt, by_output=False)

        new_node = Norm(
            name=f"{node_name}_norm",
            input_shape=in_edges[0].shape,
            ord=ord_val,
            axes=axes,
            keepdims=redsum.keepdims,    # type: ignore
            history=node_history)
        new_node.set_quant(sqrt.get_quant(0), 0)

        self.nnir_graph.add_node(new_node)
        if abs_node is not None:
            self.nnir_graph.remove_node(abs_node, reconnect=False, reindex_input_edges=False)
        self.nnir_graph.remove_node(mul, reconnect=False, reindex_input_edges=False)
        self.nnir_graph.remove_node(redsum, reconnect=False, reindex_input_edges=False)
        self.nnir_graph.remove_node(sqrt, reconnect=False, reindex_input_edges=False)

        in_edge = in_edges[0]
        self.nnir_graph.add_edge(in_edge.clone(dest=new_node.name))

        for out_edge in out_edges:
            self.nnir_graph.add_edge(out_edge.clone(src=new_node.name))

    def short_name(self):
        return "frobenius_norm_substitution"
