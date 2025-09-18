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
Created on 5/24/23

@author: irenab
"""
from typing import Tuple

from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Conv2dBias
from uni.tensorflow.tf_parser.nnir_node_factory._conv2d_base import TFConv2dToNnirBase, TFConv2dOpToNnirBase
from uni.tensorflow.tf_parser.nnir_node_factory._op_weights_bias_mixin import TFOpWithWeightsBiasMixin
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode


class TFConv2dToNnir(TFConv2dToNnirBase):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Conv2D """
    tf_attr = TFConv2dOpToNnirBase.tf_attr + TFOpWithWeightsBiasMixin.tf_kernel_attrs + ['filters', 'groups']

    @classmethod
    @validate_tf(tf_attr)
    def convert(cls, tf_node: TFMetaNode) -> Tuple[Conv2dBias, GraphRequest]:
        return super()._convert(tf_node)
