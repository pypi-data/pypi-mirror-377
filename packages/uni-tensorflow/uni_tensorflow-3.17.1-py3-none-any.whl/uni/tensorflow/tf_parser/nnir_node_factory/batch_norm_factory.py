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

from uni.common.core.multigraph.node_graph_api import GraphRequest, ConstNodeCfg
from uni.common.core.nnir_graph.nnir_nodes import BatchNorm
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_node_factory import TFNodeFactory, validate_tf
from ._op_weights_bias_mixin import tf_weight_attrs


class TFBatchNormToNnir(TFNodeFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/BatchNormalization """

    @classmethod
    @validate_tf(attrs=[
        'axis', 'epsilon', 'scale', 'center', 'momentum', 'moving_mean_initializer', 'moving_variance_initializer'
    ] + tf_weight_attrs('beta') + tf_weight_attrs('gamma'))
    def convert(cls, node: TFMetaNode) -> Tuple[BatchNorm, GraphRequest]:

        axis = node.get_attr('axis')
        # convert axis from list wrapper to int
        if isinstance(axis, list):
            axis = axis[0]

        epsilon = node.get_attr('epsilon')

        scale = node.get_attr('scale')
        gamma = node.keras_layer.gamma.numpy() if scale else 1    # type: ignore

        center = node.get_attr('center')
        beta = node.keras_layer.beta.numpy() if center else 0    # type: ignore

        mean = node.keras_layer.moving_mean.numpy()    # type: ignore
        variance = node.keras_layer.moving_variance.numpy()    # type: ignore

        # here we convert the gamma, beta, mean and variance to two consts that represent the same transformation
        a, b = BatchNorm.get_a_b(gamma, beta, mean, variance, epsilon)

        const_inputs_to_add = {
            BatchNorm.Inputs.A: ConstNodeCfg(node.name + '_a', a),
            BatchNorm.Inputs.B: ConstNodeCfg(node.name + '_b', b)
        }
        request = GraphRequest(const_inputs_to_insert=const_inputs_to_add)    # type: ignore

        batch_norm_node = BatchNorm(node.name, axis=axis)
        return batch_norm_node, request
