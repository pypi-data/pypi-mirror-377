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
from abc import ABC
from typing import List, Tuple, Optional, NamedTuple

import numpy as np

import uni.tensorflow.tf_parser.tf_mct_reader_helper
from uni.common.core.multigraph.node_graph_api import ConstNodeCfg, GraphRequest
from uni.common.core.nnir_graph.nnir_nodes.weights_bias_node_base import WeightsAndBiasNodeBase
from uni.common.core.nnir_graph.quant_info import QuantInfoBase
from uni.tensorflow.tf_parser import tf_reader_helper
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode


class Weight(NamedTuple):
    np_array: Optional[np.ndarray]
    quant: Optional[QuantInfoBase]


def tf_weight_attrs(name):
    # tf trainable params have same 3 args per each param
    return [name + a for a in ['_initializer', '_regularizer', '_constraint']]


class TFOpWithWeightsBiasMixin(ABC):
    kernel_attr = 'kernel'
    bias_attr = 'bias'
    tf_bias_attrs = tf_weight_attrs(bias_attr)
    # some ops use different name for weights, so we define them separately
    tf_kernel_attrs = tf_weight_attrs(kernel_attr)

    @classmethod
    def get_kernel(cls, node: TFMetaNode) -> Weight:
        kernel = tf_reader_helper.get_kernel(node.keras_layer, cls.kernel_attr)
        quant = uni.tensorflow.tf_parser.tf_mct_reader_helper.get_quant(node.keras_layer, cls.kernel_attr)
        return Weight(np_array=kernel, quant=quant)

    @classmethod
    def get_bias(cls, node: TFMetaNode) -> Weight:
        bias = tf_reader_helper.get_bias(node.keras_layer)
        quant = uni.tensorflow.tf_parser.tf_mct_reader_helper.get_quant(node.keras_layer, cls.bias_attr)
        return Weight(np_array=bias, quant=quant)

    @classmethod
    def validate_and_query_weights(cls, node: TFMetaNode, weight_semantics, kernel_size=None):
        shapes = cls.get_input_shapes_incl_weights(node)
        return WeightsAndBiasNodeBase.validate_and_query_weights(inputs_shapes=shapes,
                                                                 weight_semantics=weight_semantics,
                                                                 kernel_size=kernel_size,
                                                                 infer_kernel_size=False)

    @staticmethod
    def get_input_data_shape(node: TFMetaNode) -> Tuple[int, ...]:
        assert node.inbound_node_index is not None
        input_shape = tf_reader_helper.get_dynamic_input_shapes(node.keras_layer, node.inbound_node_index)
        assert len(input_shape) == 1
        return input_shape[0]

    @classmethod
    def get_input_shapes_incl_weights(cls, node: TFMetaNode) -> List[tuple]:
        """ """
        input_shape = cls.get_input_data_shape(node)
        kernel = cls.get_kernel(node)
        bias = cls.get_bias(node)
        shapes = [input_shape]
        if kernel is not None:
            shapes.append(kernel.np_array.shape)    # type: ignore [union-attr]
        if bias is not None and bias.np_array is not None:
            shapes.append(bias.np_array.shape)
        return shapes

    @staticmethod
    def get_output_shape(node: TFMetaNode):
        assert node.inbound_node_index is not None
        output_shape = tf_reader_helper.get_layer_output_shapes(node.keras_layer, node.inbound_node_index)
        assert len(output_shape) == 1
        return output_shape[0]

    @classmethod
    def request_add_weight_bias(cls, node: TFMetaNode, out_channels: Optional[int] = None) -> GraphRequest:
        """ Extract weights and bias from tf layer and create GraphRequest to add them as input nodes.
            If bias is missing, zero bias is added as vector of length out_channels,
            or as s scalar if out_channels is None  """

        _kernel = cls.get_kernel(node)
        kernel = ConstNodeCfg(node.name + '_kernel', _kernel.np_array, _kernel.quant)
        _bias = cls.get_bias(node)
        if _bias.np_array is None:
            _bias = Weight(np_array=WeightsAndBiasNodeBase.zero_bias(out_channels), quant=None)
        bias = ConstNodeCfg(node.name + '_bias', _bias.np_array, _bias.quant)
        cfg = {1: kernel, 2: bias}
        return GraphRequest(const_inputs_to_insert=cfg)
