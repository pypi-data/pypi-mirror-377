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
from .nnir_node import NnirNode
from uni.common.core.error import supported_vals_msg


class TopK(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 2

    supported_is_sorted = [True]
    unsupported_is_sorted_error_msg = supported_vals_msg(supported_is_sorted)

    def __init__(self, name, k: int, is_sorted: bool, **kwargs):
        super().__init__(name, **kwargs)
        self.k = k
        self.is_sorted = is_sorted

    def _validate(self):
        if self.is_sorted not in self.supported_is_sorted:
            self.raise_op_param_error('sorted', self.is_sorted, self.unsupported_is_sorted_error_msg)

    def export_uni_model(self):
        from uni_model import UniLayerTopK
        return UniLayerTopK(self.name, k=self.k, sorted=self.is_sorted, out_dtypes=self.get_uni_model_out_dtypes())
