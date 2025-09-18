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
Created on 1/8/23

@author: irenab
"""
from dataclasses import replace
from typing import Tuple

from uni.common.core.error import raise_op_param_error
from uni.common.core.nnir_graph.nnir_nodes import Conv2dBias
from uni.common.core.nnir_graph.quant_info import QuantPerChannelBase
from uni.common.core.nnir_graph.semantics import AxisSemantics
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from ._conv2d_base import TFConv2dToNnirBase
from ._op_weights_bias_mixin import tf_weight_attrs, Weight
from .tf_node_factory import validate_tf


class TFDepthwiseConv2dToNnir(TFConv2dToNnirBase):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/DepthwiseConv2D """
    tf_attr = TFConv2dToNnirBase.tf_attr + ['depth_multiplier', 'groups'] + tf_weight_attrs('depthwise')
    kernel_attr = "depthwise_kernel"
    k_q_per_channel_with_dm_error_msg = "depth_multiplier is limited to 1 when kernel quant per channel is True"

    @classmethod
    @validate_tf(tf_attr)
    def convert(cls, tf_node: TFMetaNode) -> Tuple[Conv2dBias, GraphRequest]:
        return super()._convert(tf_node)

    @staticmethod
    def channel_axis_err_msg(valid_axes):
        return f"depthwise_kernel channel axis must be one of {valid_axes}"

    @classmethod
    def get_kernel(cls, node: TFMetaNode) -> Weight:
        kernel = super().get_kernel(node)
        assert kernel.np_array is not None    # for mypy
        # dw weights are (h, w, ci, dm)
        # to match conv2d weight semantics we reshape into (h, w, 1, ci*
        shape = list(kernel.np_array.shape)
        ci_axis = cls.tf_weight_semantics.axis_by_semantics(AxisSemantics.IN_CHANNELS)
        co_axis = cls.tf_weight_semantics.axis_by_semantics(AxisSemantics.OUT_CHANNELS)
        shape[ci_axis] = 1
        shape[co_axis] = -1

        if isinstance(kernel.quant, QuantPerChannelBase):
            dm = node.get_attr("depth_multiplier")
            if dm > 1:
                raise_op_param_error(cls.tf_op_info(node), "depth_multiplier", dm,
                                     cls.k_q_per_channel_with_dm_error_msg, None)

            ci_axes = [ci_axis, ci_axis - 4]
            if kernel.quant.axis not in ci_axes:
                raise_op_param_error(cls.tf_op_info(node), "channel_axis", kernel.quant.axis,
                                     cls.channel_axis_err_msg(ci_axes), None)
            quant = replace(kernel.quant, axis=co_axis)
            kernel = Weight(np_array=kernel.np_array, quant=quant)
        kernel = Weight(np_array=kernel.np_array.reshape(shape), quant=kernel.quant)    # type: ignore [union-attr]
        return kernel
