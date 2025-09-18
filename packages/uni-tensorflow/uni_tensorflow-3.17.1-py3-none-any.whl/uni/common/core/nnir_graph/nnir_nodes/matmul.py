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
from typing import List

from uni.common.core.error import ParamErrorInfo, OpInputErrorInfo, raise_op_error, exceeds_limit_msg, ErrorInfo
from .nnir_node import NnirNode


class Matmul(NnirNode):
    NUM_INPUTS = 2
    NUM_OUTPUTS = 1

    max_dim_size = 2**12 - 1
    invalid_dim_size_left = exceeds_limit_msg('Dimension size on the last axis', max_dim_size)
    invalid_dim_size_right = exceeds_limit_msg('Dimension size', max_dim_size)
    invalid_transpose_error = 'Transpose flag is not supported'
    unsupported_inputs_error = 'Only dynamic 2d inputs (N, D0, D1) are supported'

    def __init__(self, name, transpose_a: bool, transpose_b: bool, **kwargs):
        super().__init__(name, **kwargs)
        self.transpose_a = transpose_a
        self.transpose_b = transpose_b

    def _validate(self):
        errors: List[ErrorInfo] = []
        if self.transpose_a is True:
            errors.append(ParamErrorInfo('transpose_a', self.transpose_a, reason=self.invalid_transpose_error))

        if self.transpose_b is True:
            errors.append(ParamErrorInfo('transpose_b', self.transpose_b, reason=self.invalid_transpose_error))

        for i, s in enumerate(self.graph_ctx.get_in_shapes()):
            reason = None
            if s[0] not in self.valid_batch or len(s) != 3:
                reason = self.unsupported_inputs_error
            elif i == 0 and s[-1] > self.max_dim_size:
                reason = self.invalid_dim_size_left
            elif i == 1 and any(d > self.max_dim_size for d in s[1:]):
                reason = self.invalid_dim_size_right
            if reason:
                in_node: NnirNode = self.graph_ctx.get_in_nodes()[i]
                errors.append(OpInputErrorInfo(input_index=i, input_name=in_node.name, reason=reason))

        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerMatmul
        return UniLayerMatmul(self.name,
                              transpose_a=self.transpose_a,
                              transpose_b=self.transpose_b,
                              out_dtypes=self.get_uni_model_out_dtypes())
