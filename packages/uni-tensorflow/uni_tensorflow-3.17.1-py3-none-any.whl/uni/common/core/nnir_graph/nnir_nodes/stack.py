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

from .nnir_node import NnirNode
from uni.common.core.error import raise_op_error, ParamErrorInfo, ErrorInfo


class Stack(NnirNode):
    NUM_INPUTS = None
    NUM_OUTPUTS = 1

    invalid_axis_error = 'Stack along batch axis is not allowed'

    def __init__(self, name, axis: int, **kwargs):
        super().__init__(name, **kwargs)
        self.axis = axis

    def _validate(self):
        num_inputs = self.graph_ctx.get_in_degree()
        ret = [self.validate_batch(input_index=i, return_error=True) for i in range(num_inputs)]
        errors: List[ErrorInfo] = [r for r in ret if r is not None]

        rank = len(self.graph_ctx.get_in_shapes()[0])
        if self.axis in [0, -(rank + 1)]:
            errors.append(ParamErrorInfo(name='axis', value=self.axis, reason=self.invalid_axis_error))

        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerStack
        return UniLayerStack(self.name, axis=self.axis, out_dtypes=self.get_uni_model_out_dtypes())
