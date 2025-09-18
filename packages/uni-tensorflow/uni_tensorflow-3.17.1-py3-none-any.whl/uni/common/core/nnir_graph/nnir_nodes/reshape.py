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
Created on 8/7/22

@author: irenab
"""
from typing import List

import numpy as np

from uni.common.core.error.util import supported_vals_msg, raise_op_error, ErrorInfo
from uni.common.core.error.defs import ParamErrorInfo
from .nnir_node import NnirNode


class Reshape(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    supported_target_batch_vals = list(set(NnirNode.valid_batch + [-1]))
    error_target_batch = 'Invalid batch dim. ' + supported_vals_msg(supported_target_batch_vals)
    error_changing_batch = 'Cannot change batch dim'

    def __init__(self, name, target_shape: tuple, **kwargs):
        super().__init__(name, **kwargs)
        # incl batch
        self.target_shape = target_shape

    def _validate(self):
        errs: List[ErrorInfo] = []
        err = self.validate_batch(input_index=0, return_error=True)
        if err:
            errs.append(err)

        if self.target_shape[0] not in self.supported_target_batch_vals:
            errs.append(ParamErrorInfo(name='target shape', value=self.target_shape, reason=self.error_target_batch))

        if self.target_shape[0] == -1:
            input_shape = self.graph_ctx.get_in_shapes()[0]
            input_size = np.prod(input_shape[1:])
            target_size = np.prod(self.target_shape[1:])
            if input_size != target_size:
                errs.append(
                    ParamErrorInfo(name='target shape', value=self.target_shape, reason=self.error_changing_batch))

        if errs:
            raise_op_error(self.op_info(), errors=errs, history=self.history)

    def get_target_full_shape(self):
        shape = list(self.target_shape)
        if shape[0] is None:
            shape[0] = int(self.batch_size)
        shape = [int(i) for i in shape]
        return shape

    def export_uni_model(self):
        from uni_model import UniLayerReshape, shape_of
        shape = shape_of(*self.get_target_full_shape(), neg_dim_allowed=True)
        return UniLayerReshape(self.name, shape=shape, out_shapes=[shape], out_dtypes=self.get_uni_model_out_dtypes())
