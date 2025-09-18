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
Created on 1/11/23

@author: irenab
"""
from typing import Tuple

import numpy as np

from uni.common.core.multigraph.node_graph_api import GraphRequest, ConstNodeCfg
from uni.common.core.nnir_graph.nnir_nodes import LayerNorm
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_node_factory import TFNodeFactory, validate_tf
from ._op_weights_bias_mixin import tf_weight_attrs


class TFLayerNormToNnir(TFNodeFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/LayerNormalization """

    @classmethod
    @validate_tf(attrs=['axis', 'epsilon', 'scale', 'center'] + tf_weight_attrs('beta') + tf_weight_attrs('gamma'))
    def convert(cls, node: TFMetaNode) -> Tuple[LayerNorm, GraphRequest]:
        axes = node.get_attr('axis')
        # As of tf2.11, tf always passes ListWrapper (with positive value), but no reason to fail if int is ever passed
        axes = [axes] if isinstance(axes, int) else list(axes)

        epsilon = node.get_attr('epsilon')

        scale = node.get_attr('scale')
        if scale:
            gamma = node.keras_layer.gamma.numpy()    # type: ignore
        else:
            gamma = np.array([1.], dtype=np.float32)

        center = node.get_attr('center')
        if center:
            beta = node.keras_layer.beta.numpy()    # type: ignore
        else:
            beta = np.array([0.], dtype=np.float32)

        const_inputs_to_add = {
            LayerNorm.Inputs.Gamma: ConstNodeCfg(node.name + '_gamma', gamma),
            LayerNorm.Inputs.Beta: ConstNodeCfg(node.name + '_beta', beta)
        }
        request = GraphRequest(const_inputs_to_insert=const_inputs_to_add)    # type: ignore

        nnir_node = LayerNorm(node.name, axes=axes, center=center, scale=scale, epsilon=epsilon)
        return nnir_node, request
