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
"""
Created on 11/7/23

@author: irenab
"""
from typing import Tuple

import numpy as np

from uni.common.core.multigraph.node_graph_api import GraphRequest, ConstNodeCfg
from uni.common.core.nnir_graph.nnir_nodes import FasterRCNNBoxDecode
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory, validate_tf


class TFFasterRCNNBoxDecodeToNnir(TFNodeFactory):

    @classmethod
    @validate_tf(attrs=['anchors', 'scale_factors', 'clip_window', 'custom_version'])
    def convert(cls, tf_node: TFMetaNode) -> Tuple[FasterRCNNBoxDecode, GraphRequest]:
        anchors = np.asarray(tf_node['anchors']).astype(np.float32)
        scale_factors = tuple(map(float, tf_node['scale_factors']))
        clip_window = tuple(map(float, tf_node['clip_window']))
        nnir_node = FasterRCNNBoxDecode(tf_node.name, scale_factors=scale_factors, clip_window=clip_window)

        const_cfg = ConstNodeCfg(tf_node.name + '/anchors', data=anchors)
        request = GraphRequest(const_inputs_to_insert={FasterRCNNBoxDecode.Inputs.Anchors: const_cfg})

        return nnir_node, request
