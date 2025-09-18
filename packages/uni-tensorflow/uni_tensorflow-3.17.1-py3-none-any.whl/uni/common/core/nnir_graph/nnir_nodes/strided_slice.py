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
from typing import List

from .nnir_node import NnirNode
from uni.common.core.error import exceeds_limit_msg, ParamErrorInfo, raise_op_error, ErrorInfo


class StridedSlice(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    max_stride = 4065
    invalid_stride_limit_error = exceeds_limit_msg('Stride', max_stride)
    invalid_negative_stride_error = 'Only positive stride is supported'

    def __init__(self, name, begin: List[int], end: List[int], strides: List[int], begin_mask: int, end_mask: int,
                 **kwargs):
        super().__init__(name, **kwargs)
        assert len(begin) == len(end) == len(strides)
        self.begin = begin
        self.end = end
        self.strides = strides
        self.begin_mask = begin_mask
        self.end_mask = end_mask

    def _validate(self):
        errors: List[ErrorInfo] = []
        ndims = len(self.graph_ctx.get_in_shapes()[0])
        assert ndims == len(self.begin)

        if self.strides[1] > self.max_stride and ndims == 2:
            errors.append(ParamErrorInfo('stride', self.strides, self.invalid_stride_limit_error))

        if any([s <= 0 for s in self.strides]):
            errors.append(ParamErrorInfo('stride', self.strides, self.invalid_negative_stride_error))

        err = self.validate_batch(input_index=0, return_error=True)
        if err:
            errors.append(err)

        if errors:
            raise_op_error(self.op_info(), errors, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerStrideSlice
        return UniLayerStrideSlice(self.name,
                                   begin=[int(v) for v in self.begin],
                                   end=[int(v) for v in self.end],
                                   stride=[int(v) for v in self.strides],
                                   begin_mask=self.begin_mask,
                                   end_mask=self.end_mask,
                                   ellipsis_mask=0,
                                   new_axis_mask=0,
                                   shrink_axis_mask=0,
                                   out_dtypes=self.get_uni_model_out_dtypes())

    @staticmethod
    def calculate_mask(axes):
        """ Convenience method for factories. LSB corresponds to axis 0 """
        return sum([1 << i for i in axes])
