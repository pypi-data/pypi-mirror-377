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
Created on 12/28/22

@author: irenab
"""
import abc
from typing import Optional
import tensorflow as tf

from uni.common.core.multigraph.node_graph_api import NodeToInsertCfg, NodePosition
from uni.common.core.nnir_graph.nnir_nodes import ReluX, Sigmoid, Swish, Tanh
from uni.common.core.error.util import supported_vals_msg, raise_op_param_error
from uni.common.core.nnir_graph.nnir_nodes.gelu import Gelu
from uni.common.core.nnir_graph.nnir_nodes.hard_sigmoid import HardSigmoid
from uni.common.core.node_history import NodeHistory
from uni.tensorflow.tf_parser import tf_reader_helper
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory, TFMetaNode


def get_tf_hard_sigmoid_by_version():
    from packaging import version
    ver = version.parse(tf.__version__)
    if ver < version.parse("2.16.0"):
        # https://www.tensorflow.org/versions/r2.15/api_docs/python/tf/keras/activations/hard_sigmoid
        return lambda **kwargs: HardSigmoid(**kwargs, alpha=0.2, beta=0.5)
    else:
        raise ValueError(f"cannot use hard_sigmoid with TensorFlow version {ver}")


# activations inside tf op
tf_op_activation_to_nnir = {
    None: None,
    'linear': None,
    'relu': lambda **kwargs: ReluX(**kwargs, x=None),
    'gelu': lambda **kwargs: Gelu(**kwargs, approximate=False),
    'sigmoid': Sigmoid,
    'hard_sigmoid': get_tf_hard_sigmoid_by_version(),
    'swish': Swish,
    'tanh': Tanh,
}


class TFOpWithActivationMixin(abc.ABC):
    tf_activation_attrs = ['activation', 'activity_regularizer']

    invalid_activation_error = supported_vals_msg(list(tf_op_activation_to_nnir.keys()))

    @classmethod
    def process_activation(cls, tf_node: TFMetaNode) -> Optional[NodeToInsertCfg]:
        activation = tf_node.get_attr('activation')
        op_info = TFNodeFactory.tf_op_info(tf_node)
        if activation not in tf_op_activation_to_nnir:
            raise_op_param_error(op_info,
                                 param_name='activation',
                                 param_value=activation,
                                 reason=cls.invalid_activation_error,
                                 history=None)

        activ_factory = tf_op_activation_to_nnir[activation]
        if activ_factory is None:
            return None

        history = NodeHistory(op_info, desc='Extract activation')
        name = tf_node.name + '_activation'
        activ_node = activ_factory(name=name, history=history)
        assert tf_node.inbound_node_index is not None
        output_shape = tf_reader_helper.get_layer_output_shapes(tf_node.keras_layer, tf_node.inbound_node_index)[0]
        return NodeToInsertCfg(node=activ_node, shape=output_shape, node_position=NodePosition.NODE_AFTER)
