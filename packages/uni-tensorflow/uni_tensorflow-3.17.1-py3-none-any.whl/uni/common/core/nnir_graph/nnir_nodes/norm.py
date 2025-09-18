# -------------------------------------------------------------------------------
# (c) Copyright 2024 Sony Semiconductor Israel, Ltd. All rights reserved.
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
Created on 8/29/24

@author: lotanw
"""
from typing import List, Tuple

from uni.common.core.error import ErrorInfo, ParamErrorInfo, raise_op_error, supported_vals_msg, OpInputErrorInfo
from uni.common.core.nnir_graph.nnir_nodes import NnirNode


class Norm(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    supported_ord_values = [2, "fro", "euclidean"]
    unsupported_ord_err_msg = supported_vals_msg(supported_ord_values)
    min_dims_err_msg = "input shape rank must have at least two other dimensions not stated in axes list"
    all_axes_err_msg = "norm on all axes is not supported"

    def __init__(self, name, input_shape: Tuple[int, ...], ord, axes: List[int], keepdims: bool = False, **kwargs):
        super().__init__(name, **kwargs)
        self.input_shape = input_shape
        self.ord = ord
        self.axes = axes
        self.keepdims = keepdims

    def _batch_validate(self):
        error = None
        for i in self.axes:
            error = self.validate_non_batch_op_axis(i, return_error=True)
            if error is not None:
                break
        return error

    def _validate(self):
        errors: List[ErrorInfo] = []
        if self.axes is None or len(self.axes) == len(self.input_shape):
            errors.append(ParamErrorInfo(name='axes', value=self.axes, reason=Norm.all_axes_err_msg))
        else:
            batch_error = self._batch_validate()
            if batch_error is not None:
                errors.append(batch_error)
            # BE limitation, input shape must have at least two more dimensions other than the stated dimensions in axis
            if len(self.input_shape) < 2 + len(self.axes):
                errors.append(OpInputErrorInfo(input_index=0, input_name="input", reason=Norm.min_dims_err_msg))
        if self.ord not in self.supported_ord_values:
            errors.append(ParamErrorInfo(name='ord', value=self.ord, reason=self.unsupported_ord_err_msg))
        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerNorm
        return UniLayerNorm(self.name,
                            axes=self.axes,
                            keep_dims=self.keepdims,
                            out_dtypes=self.get_uni_model_out_dtypes())
