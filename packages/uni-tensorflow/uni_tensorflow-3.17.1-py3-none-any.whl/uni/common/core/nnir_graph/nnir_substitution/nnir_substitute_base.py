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
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple, Callable

from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.uid_generator import UIDGenerator
from uni.common.util.vis import MultigraphVis    # type: ignore


class NnirSubstituteBase(ABC):

    def __init__(self, nnir_graph, vis_dir: Optional[Path]):
        self.nnir_graph = nnir_graph
        self.vis_dir = vis_dir

    @abstractmethod
    def get_match_list(self) -> List[List[NnirNode]]:
        pass

    @abstractmethod
    def single_match_substitute(self, match: List[NnirNode]):
        pass

    @abstractmethod
    def short_name(self):
        pass

    @staticmethod
    def get_new_name(old_node: NnirNode):
        return f"{old_node.name}_uid{UIDGenerator.next()}"

    def dev_post_validation(self):
        self.nnir_graph.validate_graph(allow_disconnected_outputs=False)
        self.nnir_graph.validate_nodes()

    def substitute(self):
        match_list = self.get_match_list()
        for match in match_list:
            self.single_match_substitute(match)
        if self.vis_dir:    # pragma: no cover
            MultigraphVis.dump_vis_json(self.nnir_graph, self.vis_dir / f"after_{self.short_name()}.json")

    selectors_func_type = Optional[Callable[[NnirNode, NnirGraph], bool]]
    nodes_op_selectors_type = List[Tuple[Optional[type], selectors_func_type]]

    def nodes_linear_op_matcher(self, nodes_op_and_selector: nodes_op_selectors_type) -> List[List[NnirNode]]:
        result = []
        for node in self.nnir_graph.topological_sort(data=True):
            r = self.node_linear_op_matcher(node, nodes_op_and_selector)
            if r is not None:
                result.extend(r)
        return result

    def node_linear_op_matcher(self, node: NnirNode, nodes_op_and_selectors: nodes_op_selectors_type) \
            -> Optional[List[List[NnirNode]]]:
        assert len(nodes_op_and_selectors) > 0
        result = [[]]    # type: List[List[NnirNode]]
        potential_nodes = [node]
        for node_type, node_selector in nodes_op_and_selectors:
            found_op = [n for n in potential_nodes if node_type is None or isinstance(n, node_type)]
            matched_nodes = [n for n in found_op if node_selector is None or node_selector(n, self.nnir_graph)]
            if not matched_nodes:
                return None
            result = [r + [new_node] for r, new_node in zip(result * len(matched_nodes), matched_nodes)]
            potential_nodes = [
                node for r in matched_nodes for node in self.nnir_graph.get_out_nodes(r, by_output=False, data=True)
            ]
        return result
