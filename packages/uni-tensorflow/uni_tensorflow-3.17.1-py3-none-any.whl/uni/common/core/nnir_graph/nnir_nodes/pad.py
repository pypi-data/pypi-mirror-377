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
Created on 12/29/22

@author: irenab
"""
from typing import List

import numpy as np

from uni.common.core.error import ParamErrorInfo, raise_op_error, ErrorInfo
from .nnir_node import NnirNode


class Pad(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    invalid_batch_pad = 'Padding for batch dim is not supported'

    def __init__(self, name, paddings: np.ndarray, pad_const: float, **kwargs):
        """ paddings: array of shape (ndims, 2). paddings[i] is (pre-pad, post-pad) for axis i
            Paddings length should be same as input shape length (including batch axis) """
        super().__init__(name, **kwargs)
        if len(paddings.shape) != 2 or paddings.shape[1] != 2:
            raise RuntimeError('Invalid paddings passed, expected array of shape (ndims, 2)')

        self.paddings = paddings
        self.pad_const = pad_const

    def _validate(self):
        if len(self.graph_ctx.get_in_shapes()[0]) != len(self.paddings):
            raise RuntimeError('Paddings length does not match the input shape length')

        errors: List[ErrorInfo] = []
        err = self.validate_batch(input_index=0, return_error=True)
        if err:
            errors.append(err)
        if any(self.paddings[0] > 0):
            errors.append(ParamErrorInfo(name='paddings', value=self.paddings, reason=self.invalid_batch_pad))

        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def is_identity(self) -> bool:
        return not np.any(self.paddings)

    def export_uni_model(self):
        from uni_model import UniLayerPad, Pair
        pad_list = [Pair(int(self.paddings[i][0]), int(self.paddings[i][1])) for i in range(self.paddings.shape[0])]
        return UniLayerPad(self.name,
                           pad_list=pad_list,
                           constant_values=float(self.pad_const),
                           out_dtypes=self.get_uni_model_out_dtypes())
