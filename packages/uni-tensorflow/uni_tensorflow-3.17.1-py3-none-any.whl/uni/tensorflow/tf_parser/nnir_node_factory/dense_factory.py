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
Created on 1/9/23

@author: irenab
"""
from typing import Tuple, Optional

from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeToInsertCfg
from uni.common.core.nnir_graph.nnir_nodes import FullyConnected
from uni.common.core.nnir_graph.semantics import TensorSemantics, AxisSemantics
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_node_factory import TFNodeFactory, validate_tf
from ._op_weights_bias_mixin import TFOpWithWeightsBiasMixin
from ._op_activation_mixin import TFOpWithActivationMixin


class TFDenseToNnir(TFNodeFactory, TFOpWithWeightsBiasMixin, TFOpWithActivationMixin):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dense """

    tf_weight_semantics = TensorSemantics(AxisSemantics.IN_CHANNELS, AxisSemantics.OUT_CHANNELS)

    @classmethod
    @validate_tf(attrs=['units', 'use_bias'] + TFOpWithWeightsBiasMixin.tf_bias_attrs +
                 TFOpWithWeightsBiasMixin.tf_kernel_attrs + TFOpWithActivationMixin.tf_activation_attrs)
    def convert(cls, node: TFMetaNode) -> Tuple[FullyConnected, GraphRequest]:

        has_bias, (out_channels, _), _ = cls.validate_and_query_weights(node, cls.tf_weight_semantics, kernel_size=None)
        assert has_bias == node.get_attr('use_bias')
        assert out_channels == node.get_attr('units')

        fc = FullyConnected(node.name, cls.get_history(node))
        fc.weight_semantics = cls.tf_weight_semantics

        request = cls.request_add_weight_bias(node, out_channels)

        request_activ: Optional[NodeToInsertCfg] = cls.process_activation(node)
        if request_activ:
            request.adjacent_node_to_insert = request_activ

        return fc, request
