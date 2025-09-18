# -------------------------------------------------------------------------------
# (c) Copyright 2023 Sony Semiconductor Israel, Ltd. All rights reserved.
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
from typing import List, Tuple

from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Variable
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase
from uni.common.logger import get_logger

logger = get_logger(__name__)


class RemoveIdentityLikeSubstitution(NnirSubstituteBase):
    """ Remove identity-like (no-op) nodes - any node instance for which node.is_identity() returns True.
        It is expected to be a unary or binary node with a single output. If binary, exactly one of the
        inputs is expected to be const.
        Any additional info on edges (quant, semantics) should be added after this stage, otherwise it can be lost.

        There are two ways of handling no-op ops:
        * at framework factory level - create Identity directly
        * at NnirNode level - intended for ops that become identity only with certain params/inputs and
                              are not framework-specific
    """

    def short_name(self):
        return 'remove_identity_like'

    def get_match_list(self) -> List[List[NnirNode]]:

        def selector(node: NnirNode, graph: NnirGraph):
            return node.is_identity()

        return self.nodes_linear_op_matcher([(None, selector)])

    def single_match_substitute(self, match: List[NnirNode]):

        def find_const_input(input_nodes) -> Tuple[Variable, int]:
            const_indices = [i for i, n in enumerate(input_nodes) if isinstance(n, Variable)]
            if len(const_indices) != 1:
                raise RuntimeError(f'Expected binary op with exactly 1 input const {node.op}, got {len(const_indices)}')
            index = const_indices[0]
            return input_nodes[index], index

        assert len(match) == 1
        node = match[0]

        logger.debug(f'Removing no-op {node}')
        input_nodes: List[NnirNode] = self.nnir_graph.get_ordered_in_nodes(node, data=True)
        if len(input_nodes) not in [1, 2]:
            raise RuntimeError(f'Expected unary or binary op, got {len(input_nodes)} inputs')
        if len(input_nodes) == 2:
            const, input_index = find_const_input(input_nodes)
            self.nnir_graph.remove_edge(const.name, 0, node.key, input_index)
            self.nnir_graph.remove_node_if_detached(const)
            self.nnir_graph.reindex_in_edges(node)
        self.nnir_graph.remove_node(node, reconnect=True, reindex_input_edges=False)
