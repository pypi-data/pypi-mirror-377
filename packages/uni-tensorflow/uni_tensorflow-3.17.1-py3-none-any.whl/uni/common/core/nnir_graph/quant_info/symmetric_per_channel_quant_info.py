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

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from uni.common.core.nnir_graph.quant_info import QuantPerChannelBase


@dataclass(frozen=True)
class SymmetricPerChannelQuantInfo(QuantPerChannelBase):
    thresholds: Tuple[float, ...]
    signed: bool

    def export_uni_model(self):
        # convert to float for safety reasons
        from uni_model import QtypePerAxis, MinMaxOpenEnded, QtypePerTensor
        if self.signed:
            min_maxes = [MinMaxOpenEnded.from_open_symmetric_threshold(float(th)) for th in self.thresholds]
        else:
            min_maxes = [MinMaxOpenEnded.from_open_positive_threshold(float(th)) for th in self.thresholds]

        if len(min_maxes) == 1:
            return QtypePerTensor(value_n_bits=self.value_n_bits, min_max=min_maxes[0])
        return QtypePerAxis(value_n_bits=self.value_n_bits, axis=self.axis, min_maxes=min_maxes)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, SymmetricPerChannelQuantInfo):
            return False
        return (np.allclose(self.thresholds, other.thresholds) and self.value_n_bits == other.value_n_bits
                and self.signed == other.signed and self.axis == other.axis)
