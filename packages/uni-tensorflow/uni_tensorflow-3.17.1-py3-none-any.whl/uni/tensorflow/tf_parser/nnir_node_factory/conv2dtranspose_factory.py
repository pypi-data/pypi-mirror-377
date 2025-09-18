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
Created on 5/18/23

@author: irenab
"""
from typing import Tuple

from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Conv2dTransposeBias
from uni.common.core.nnir_graph.nnir_nodes.common import Padding2d, Param2d
from uni.common.core.nnir_graph.semantics import TensorSemantics, AxisSemantics
from uni.common.core.error import raise_op_param_error, supported_vals_msg
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import validate_tf
from ._conv2d_base import TFConv2dOpToNnirBase, ConvParams, TFOpWithWeightsBiasMixin


class TFConv2dTransposeToNnir(TFConv2dOpToNnirBase):
    tf_attr = TFConv2dOpToNnirBase.tf_attr + TFOpWithWeightsBiasMixin.tf_kernel_attrs + \
              ['filters', 'output_padding', 'groups']

    tf_weight_semantics = TensorSemantics(AxisSemantics.KERNEL_H,
                                          AxisSemantics.KERNEL_W,
                                          AxisSemantics.OUT_CHANNELS,
                                          AxisSemantics.IN_CHANNELS)  # yapf: disable

    valid_padding = 'valid'
    invalid_padding_error = 'Unsupported padding. ' + supported_vals_msg([valid_padding])

    @classmethod
    @validate_tf(attrs=tf_attr)
    def convert(cls, tf_node: TFMetaNode) -> Tuple[Conv2dTransposeBias, GraphRequest]:
        return super()._convert(tf_node)

    @classmethod
    def _convert_op(cls, tf_node: TFMetaNode, params: ConvParams) -> Conv2dTransposeBias:
        groups = tf_node.get_attr('groups')
        # Currently (tf2.12) tf doesn't support grouped convtranspose,
        # however if it's passed as kwarg no error is raised.
        if groups != 1:
            raise ValueError(f'Unexpected groups {groups} for Conv2DTranspose keras layer')

        tf_out_pad = tf_node.get_attr('output_padding')
        nnir_out_pad = Param2d(*tf_out_pad) if tf_out_pad is not None else Param2d(0, 0)

        nnir_pad = Padding2d((0, 0), (0, 0))
        if params.padding != cls.valid_padding:
            # Nnir node already does the validation but it expects a numeric padding.
            # The calculation is not trivial and must be tested, so instead we validate it separately here
            raise_op_param_error(cls.tf_op_info(tf_node),
                                 'padding',
                                 params.padding,
                                 reason=TFConv2dTransposeToNnir.invalid_padding_error,
                                 history=None)

        node = Conv2dTransposeBias(tf_node.name,
                                   kernel_size=params.kernel_size,
                                   stride=params.stride,
                                   dilation=params.dilation,
                                   groups=groups,
                                   pad=nnir_pad,
                                   out_pad=nnir_out_pad)
        return node
