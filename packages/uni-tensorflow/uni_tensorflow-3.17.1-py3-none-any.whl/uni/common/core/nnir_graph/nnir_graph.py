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
from typing import Iterable, Optional, Sequence

from uni.common.core.error.defs import InvalidOpError, InvalidOpsError
from uni.common.core.multigraph.graph import MultiDiGraph
from uni.common.logger import get_logger, MessageCodes
from uni.common.util.dev import skip_compliance_check
from .nnir_edge import NnirEdge
from .nnir_nodes import NnirNode
from .semantics import DataFormat, SemanticsHelper

logger = get_logger(__name__)


class NnirGraph(MultiDiGraph[NnirNode, NnirEdge]):
    """ Graph containing NnirNodes and NnirEdges """

    def __init__(self,
                 data_format: DataFormat,
                 nodes: Optional[Iterable[NnirNode]] = None,
                 edges: Optional[Iterable[NnirEdge]] = None):
        super().__init__(nodes=nodes, edges=edges)
        self.data_format = data_format

    def add_node(self, node, inject_ctx: bool = True) -> None:
        super().add_node(node)
        if inject_ctx:
            node.graph_ctx = self.get_graph_context_for_node(node)

    def add_nodes(self, nodes: Sequence[NnirNode], inject_ctx: bool = True):
        for n in nodes:
            self.add_node(n, inject_ctx)

    def validate_nodes(self):
        if skip_compliance_check():
            logger.warning('SDSP compliance validation is disabled', message_code=MessageCodes.EXECUTION)
            return
        else:
            logger.debug('Running SDSP compliance validation')
        invalid_nodes = []
        for node in self.get_nodes(data=True):    # type: NnirNode
            try:
                node.validate()
            except InvalidOpError as e:
                invalid_nodes.append(e.op_errors)
        if invalid_nodes:
            raise InvalidOpsError(invalid_nodes)

    def set_semantics_on_nodes(self):
        semantics_helper = SemanticsHelper(self.data_format)
        for node in self.topological_sort(data=True):    # type: NnirNode
            input_semantics = node.get_input_semantics(semantics_helper)
            if input_semantics:
                in_edges: list = self.get_ordered_in_edges(node)
                assert len(in_edges) == len(input_semantics)
                for input_edge, tensor_sem in zip(in_edges, input_semantics):
                    if tensor_sem is None:
                        continue

                    prev_node: NnirNode = self.get_node_data(input_edge.src)
                    prev_node.set_semantics(tensor_sem, input_edge.src_index)

            node.set_output_semantics(semantics_helper)
