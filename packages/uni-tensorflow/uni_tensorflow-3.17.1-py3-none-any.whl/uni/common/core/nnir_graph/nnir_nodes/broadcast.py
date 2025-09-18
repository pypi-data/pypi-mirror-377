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
from typing import List, Tuple, Union

from uni.common.core.error import ErrorInfo, ParamErrorInfo, supported_vals_msg, raise_op_error
from uni.common.core.nnir_graph.nnir_nodes import NnirNode


class Broadcast(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    error_target_batch = 'Invalid batch dim. ' + supported_vals_msg([1])
    error_empty_shape = 'Invalid shape 0 is not supported is shape '

    def __init__(self, name, shape: Union[List[int], Tuple[int, ...]], **kwargs):
        super().__init__(name, **kwargs)
        self.shape = shape

    def _validate(self):
        errs: List[ErrorInfo] = []
        if self.shape[0] != 1:
            errs.append(ParamErrorInfo(name='shape', value=self.shape, reason=self.error_target_batch))
        if 0 in self.shape:
            errs.append(ParamErrorInfo(name='shape', value=self.shape, reason=self.error_empty_shape))
        if errs:
            raise_op_error(self.op_info(), errors=errs, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerBroadcast, shape_of
        shape = shape_of(*[int(i) for i in self.shape])
        return UniLayerBroadcast(self.name, shape=shape, out_shapes=[shape], out_dtypes=self.get_uni_model_out_dtypes())
