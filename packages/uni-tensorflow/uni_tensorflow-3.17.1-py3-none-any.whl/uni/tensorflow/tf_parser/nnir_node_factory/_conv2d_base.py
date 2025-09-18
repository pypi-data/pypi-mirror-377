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
Created on 12/21/22

@author: irenab
"""
from typing import Tuple, Optional, NamedTuple, TypeVar
import abc

from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeToInsertCfg
from uni.common.core.nnir_graph.nnir_nodes import Conv2dBias, NnirNode
from uni.common.core.nnir_graph.nnir_nodes.common import Padding2d, Param2d
from uni.common.core.nnir_graph.semantics import TensorSemantics, AxisSemantics
from uni.common.parsers._pad_util import calc_same_padding, ExcessPaddingLocation
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory
from ._op_weights_bias_mixin import TFOpWithWeightsBiasMixin
from ._op_activation_mixin import TFOpWithActivationMixin
from ._op2d_mixin import TFOp2dMixin

NnirNodeT = TypeVar('NnirNodeT', bound=NnirNode)


class ConvParams(NamedTuple):
    kernel_size: Param2d
    stride: Param2d
    dilation: Param2d
    padding: str
    use_bias: bool
    w_channels_in: int
    w_channels_out: int


class TFConv2dOpToNnirBase(TFNodeFactory, TFOpWithWeightsBiasMixin, TFOpWithActivationMixin, TFOp2dMixin, abc.ABC):
    """ Base class for parsing tf conv ops - any layer that has the common attributes + bias + activation """
    tf_attr = [
        'kernel_size', 'use_bias', 'strides', 'dilation_rate', 'padding', *TFOpWithWeightsBiasMixin.tf_bias_attrs,
        *TFOpWithActivationMixin.tf_activation_attrs, *TFOp2dMixin.tf_op2d_attrs
    ]
    tf_weight_semantics: TensorSemantics

    @classmethod
    def _convert(cls, tf_node: TFMetaNode) -> Tuple[NnirNodeT, GraphRequest]:

        cls.validate_data_format(tf_node)
        params = cls._parse_common_params(tf_node)

        nnir_node = cls._convert_op(tf_node, params)
        nnir_node.weight_semantics = cls.tf_weight_semantics
        nnir_node.data_format = cls.data_format

        channels_out = cls.get_output_shape(tf_node)[cls.data_format.get_c_axis()]
        request = cls.request_add_weight_bias(tf_node, channels_out)
        request_activ: Optional[NodeToInsertCfg] = cls.process_activation(tf_node)
        if request_activ:
            request.adjacent_node_to_insert = request_activ

        return nnir_node, request

    @classmethod
    @abc.abstractmethod
    def _convert_op(cls, tf_node: TFMetaNode, params: ConvParams):
        raise NotImplementedError()

    @classmethod
    def _parse_common_params(cls, node: TFMetaNode):

        def get_param2d(attr):
            return Param2d(*node.get_attr(attr))

        kernel_size = get_param2d('kernel_size')
        has_bias, (w_channels_out, w_channels_in), _ = cls.validate_and_query_weights(node,
                                                                                      cls.tf_weight_semantics,
                                                                                      kernel_size=kernel_size)
        assert has_bias == node.get_attr('use_bias')
        params = ConvParams(kernel_size=kernel_size,
                            stride=get_param2d('strides'),
                            dilation=get_param2d('dilation_rate'),
                            padding=node.get_attr('padding'),
                            use_bias=node.get_attr('use_bias'),
                            w_channels_in=w_channels_in,
                            w_channels_out=w_channels_out)
        return params


class TFConv2dToNnirBase(TFConv2dOpToNnirBase, abc.ABC):

    tf_weight_semantics = TensorSemantics(AxisSemantics.KERNEL_H,
                                          AxisSemantics.KERNEL_W,
                                          AxisSemantics.IN_CHANNELS,
                                          AxisSemantics.OUT_CHANNELS)  # yapf: disable

    @classmethod
    def _convert_op(cls, tf_node, params):
        input_shape = cls.get_input_data_shape(tf_node)

        # in tf 'groups' is present in all conv layers, even if not part of api, e.g. in depthwise conv it's 1
        groups = input_shape[cls.data_format.get_c_axis()] // params.w_channels_in
        # kernels for all groups are stacked together so w_chan_out = layer chan out
        out_group_size = params.w_channels_out // groups

        # get input h and w
        h, w = cls.get_hw(input_shape)
        pad2d: Padding2d = Padding2d()
        if params.padding == 'same':
            pad2d = calc_same_padding(h, w, params.kernel_size, params.stride, params.dilation,
                                      ExcessPaddingLocation.UPPER)
        conv2d = Conv2dBias(tf_node.name,
                            kernel_size=params.kernel_size,
                            stride=params.stride,
                            dilation=params.dilation,
                            group=groups,
                            pad2d=pad2d,
                            input_group_size=params.w_channels_in,
                            out_group_size=out_group_size,
                            history=cls.get_history(tf_node))
        return conv2d
