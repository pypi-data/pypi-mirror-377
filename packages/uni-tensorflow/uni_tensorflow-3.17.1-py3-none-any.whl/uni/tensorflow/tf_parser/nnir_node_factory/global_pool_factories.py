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
Created on 1/15/23

@author: irenab
"""
import abc
from typing import Tuple, Union, Type

from .tf_node_factory import TFNodeFactory, validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.common.core.nnir_graph.nnir_nodes import AveragePool2d, Squeeze
from uni.common.core.nnir_graph.nnir_nodes.common import Param2d, Padding2d
from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeToInsertCfg, NodePosition
from ._op2d_mixin import TFOp2dMixin


class TFGlobalPoolToNnirBase(TFNodeFactory, TFOp2dMixin, abc.ABC):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/GlobalAveragePooling2D """
    _nnir_op: Type

    @classmethod
    @validate_tf(attrs=['keepdims'] + TFOp2dMixin.tf_op2d_attrs)
    def convert(cls, node: TFMetaNode) -> Union[AveragePool2d, Tuple[AveragePool2d, GraphRequest]]:
        cls.validate_data_format(node)

        input_shape = cls.tf_reader_helper.get_dynamic_input_shapes(node.keras_layer, node.inbound_node_index)[0]
        kernel_size = Param2d(*cls.get_hw(input_shape))
        nnir_node = cls._nnir_op(node.name, kernel_size=kernel_size, stride=Param2d(1, 1), padding=Padding2d())
        nnir_node.data_format = cls.data_format

        if node.get_attr('keepdims'):
            return nnir_node

        # add squeeze
        hw_axes = cls.get_hw_axes()
        squeeze = Squeeze(node.name + '_squeeze',
                          squeeze_dims=hw_axes,
                          history=cls.get_history(node, 'keep_dims=False -> Squeeze'))

        # Unsqueeze h and w axes for the shape between pool and squeeze
        out_shape = list(cls.tf_reader_helper.get_layer_output_shapes(node.keras_layer, node.inbound_node_index)[0])
        assert len(out_shape) == 2
        for a in hw_axes:
            out_shape.insert(a, 1)
        request = GraphRequest(
            adjacent_node_to_insert=NodeToInsertCfg(squeeze, tuple(out_shape), node_position=NodePosition.NODE_AFTER))
        return nnir_node, request


class TFGlobalAvgPoolToNnir(TFGlobalPoolToNnirBase):
    _nnir_op = AveragePool2d
