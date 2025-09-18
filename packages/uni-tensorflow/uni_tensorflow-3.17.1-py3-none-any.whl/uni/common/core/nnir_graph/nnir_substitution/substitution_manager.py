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
from pathlib import Path
from typing import Optional

from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_substitution import RemoveIdentityLikeSubstitution, AbsorbQuantSubstitution, \
    MergeFullyConnectedAndAddSubstitution, RemoveDummyNodeSubstitution, SingleNodesSubstitution, RsqrtSubstitution, \
    NMSOutputsSubstitution, NormSubstitution, ConstTopkGatherSubstitution
from uni.common.core.nnir_graph.nnir_substitution.instance_norm_substitution import InstanceNormSubstitution
from uni.common.util.dev import is_dev

from uni.common.util.vis import MultigraphVis    # type: ignore

# The order is important.
# First remove identities, before any info is put on edges, since some edges can be removed
# Only then put quant info on nodes
# FullyConnectedAddSubstitution must be after AbsorbQuantSubstitution
# Dummy nodes were removed last so that no one has to deal with missing edges.
substitutes_class = [
    InstanceNormSubstitution,
    NMSOutputsSubstitution,
    SingleNodesSubstitution,
    RemoveIdentityLikeSubstitution,
    AbsorbQuantSubstitution,
    MergeFullyConnectedAndAddSubstitution,
    NormSubstitution,
    RsqrtSubstitution,
    ConstTopkGatherSubstitution,
]  # yapf: disable


class SubstitutionManager:

    def __init__(self, nnir_graph: NnirGraph, vis_dir: Optional[Path]):
        self.nnir_graph = nnir_graph
        self.vis_dir = vis_dir

    def substitute(self):
        for substitute_class in substitutes_class:
            substitute = substitute_class(self.nnir_graph, self.vis_dir)    # type: ignore [abstract]
            substitute.substitute()
            if is_dev():
                substitute.dev_post_validation()
        self.nnir_graph.validate_graph(allow_disconnected_outputs=False)
        self.nnir_graph.validate_nodes()

        remove_dummy = RemoveDummyNodeSubstitution(self.nnir_graph, self.vis_dir)
        remove_dummy.substitute()
        self.nnir_graph.validate_graph(allow_disconnected_outputs=True)

        if self.vis_dir:    # pragma: no cover
            MultigraphVis.dump_vis_json(self.nnir_graph, self.vis_dir / "after_substitution.json")
