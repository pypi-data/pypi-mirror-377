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
Created on 3/4/24

@author: lotanw
"""

import numpy as np

from uni.common.core.error import ParamErrorInfo, raise_op_error
from uni.common.core.nnir_graph.nnir_nodes import NnirNode


class HardSigmoid(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    wrong_alpha_error = "can only support alpha values of: [1/5 (tf), 1/6 (torch)]"
    wrong_beta_error = "can only support beta value of 1/2"

    def __init__(self, name, alpha, beta, **kwargs):
        super().__init__(name, **kwargs)
        self.alpha = alpha
        self.beta = beta

    def export_uni_model(self):
        from uni_model import UniLayerHardSigmoid
        return UniLayerHardSigmoid(self.name,
                                   alpha=self.alpha,
                                   beta=self.beta,
                                   out_dtypes=self.get_uni_model_out_dtypes())

    def _validate(self):
        errors = []
        if not np.isclose(self.alpha, 0.2) and not np.isclose(self.alpha, 1 / 6):
            errors.append(ParamErrorInfo(name='alpha', value=self.alpha, reason=self.wrong_alpha_error))
        if not np.isclose(self.beta, 0.5):
            errors.append(ParamErrorInfo(name='beta', value=self.beta, reason=self.wrong_beta_error))
        if errors:
            raise_op_error(op_info=self.op_info(), errors=errors, history=self.history)
