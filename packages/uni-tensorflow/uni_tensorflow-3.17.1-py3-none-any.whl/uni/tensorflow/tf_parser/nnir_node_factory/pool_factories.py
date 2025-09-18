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
from abc import ABC
from typing import Type

from uni.common.core.nnir_graph.nnir_nodes import AveragePool2d, MaxPool2d
from uni.common.core.nnir_graph.nnir_nodes.common import Param2d, Padding2d
from uni.common.parsers._pad_util import calc_same_padding, ExcessPaddingLocation
from uni.tensorflow.tf_parser.nnir_node_factory._op2d_mixin import TFOp2dMixin
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory, validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode


class TFBasePoolToNnir(TFNodeFactory, TFOp2dMixin, ABC):
    _nnir_op: Type

    @classmethod
    @validate_tf(attrs=['pool_size', 'strides', 'padding'] + TFOp2dMixin.tf_op2d_attrs)
    def convert(cls, node: TFMetaNode):
        cls.validate_data_format(node)

        def get_param2d(attr):
            return Param2d(*node.get_attr(attr))

        assert node.inbound_node_index is not None
        input_shape = cls.tf_reader_helper.get_dynamic_input_shapes(node.keras_layer, node.inbound_node_index)[0]
        h, w = cls.get_hw(input_shape)
        kernel_size = get_param2d('pool_size')
        stride = get_param2d('strides')

        pad2d: Padding2d = Padding2d()
        padding = node.get_attr('padding')
        if padding == "same":
            pad2d = calc_same_padding(input_h=h,
                                      input_w=w,
                                      kernel_size=kernel_size,
                                      stride=stride,
                                      dilation=Param2d(1, 1),
                                      padding_location=ExcessPaddingLocation.UPPER)

        nnir_node = cls._nnir_op(node.name, kernel_size=kernel_size, stride=stride, padding=pad2d)
        nnir_node.data_format = cls.data_format
        return nnir_node


class TFAveragePoolToNnir(TFBasePoolToNnir):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/AveragePooling2D """
    _nnir_op = AveragePool2d


class TFMaxPoolToNnir(TFBasePoolToNnir):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/MaxPool2D """
    _nnir_op = MaxPool2d
