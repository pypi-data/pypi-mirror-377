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
Created on 9/1/22

@author: irenab
"""
from typing import List

from uni.common.core.nnir_graph.semantics import Semantics, SemanticsHelper, AxisSemantics
from uni.common.core.error import ParamErrorInfo, raise_op_error, ErrorInfo
from .nnir_node import NnirNode
from .common import Param2d, Padding2d


class AveragePool2d(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    max_pool_size_per_dim = 255
    invalid_pool_size = f'Supported pool size for non-global pooling: ' \
                        f'H <= {max_pool_size_per_dim}, W <= {max_pool_size_per_dim}'

    def __init__(self, name, kernel_size: Param2d, stride: Param2d, padding: Padding2d, **kwargs):
        super().__init__(name, **kwargs)
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding

    def _validate(self):
        h_axis, w_axis = self.data_format.get_hw_axes()
        out_shape = self.graph_ctx.get_out_shapes()[0]
        if out_shape[h_axis] == 1 and out_shape[w_axis] == 1:
            return

        errors: List[ErrorInfo] = []
        # validate pool size
        if self.kernel_size.h > self.max_pool_size_per_dim or self.kernel_size.w > self.max_pool_size_per_dim:
            errors.append(ParamErrorInfo('pool size', self.kernel_size, self.invalid_pool_size))

        # validate Hin, Hout
        err = self.validate_data_dim_size(axis=AxisSemantics.HEIGHT,
                                          upper_limit=self.max_2d_op_h_size,
                                          return_error=True)
        if err:
            errors.append(err)

        if errors:
            raise_op_error(self.op_info(), errors, self.history)

    def get_input_semantics(self, semantics_helper: SemanticsHelper) -> Semantics:
        return semantics_helper.node_data_semantics()

    def set_output_semantics(self, semantics_helper: SemanticsHelper):
        self.output_semantics = semantics_helper.node_data_semantics()

    def export_uni_model(self):
        from uni_model import UniLayerAvgPool
        return UniLayerAvgPool(self.name,
                               k_h=self.kernel_size.h,
                               k_w=self.kernel_size.w,
                               s_h=self.stride.h,
                               s_w=self.stride.w,
                               p_h_before=self.padding.h[0],
                               p_h_after=self.padding.h[1],
                               p_w_before=self.padding.w[0],
                               p_w_after=self.padding.w[1],
                               data_format=self.get_uni_model_input_data_layout(),
                               out_dtypes=self.get_uni_model_out_dtypes())
