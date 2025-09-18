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

from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Variable, TopKGather
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase
from uni.common.logger import get_logger, MessageCodes

logger = get_logger(__name__)


class ConstTopkGatherSubstitution(NnirSubstituteBase):
    """
    Update a const node connected to a topk_gather node to input 0 (data)
    only in case that have rank 1 (is vector) update shape to (1, n) and topk_gather axis to 1
    """

    def get_match_list(self) -> List[List[NnirNode]]:

        def topk_gather_selector(node: NnirNode, graph: NnirGraph):
            data_node = graph.get_ordered_in_nodes(node, data=True)[0]
            if not isinstance(data_node, Variable):
                return False
            if len(data_node.shape) != 1:
                return False
            # validate const is only connected to topk_gather input 0
            if len(graph.get_out_nodes(data_node, data=False, by_output=False)) != 1:
                logger.warning(
                    f"const node {data_node.name} has more than one output skipping {self.__class__.__name__}",
                    message_code=MessageCodes.EXECUTION)
                return False
            return True

        return self.nodes_linear_op_matcher([(Variable, None), (TopKGather, topk_gather_selector)])

    def single_match_substitute(self, match: List[NnirNode]):
        const_node: Variable = match[0]    # type: ignore
        topk_gather: TopKGather = match[1]    # type: ignore
        const_node.data = const_node.data.reshape(1, -1)
        const_node.shape = (1, ) + tuple(const_node.shape)
        topk_gather.axis = 1

    def short_name(self):
        return "const_topk_gather_substitution"
