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
Created on 8/27/23

@author: irenab
"""
from typing import Sequence
from enum import IntEnum

from .nnir_node import NnirNode

USE_OLD_UNI_LAYER = True


class Inputs(IntEnum):
    Offsets = 0
    Anchors = 1


class FasterRCNNBoxDecode(NnirNode):
    Inputs = Inputs

    NUM_INPUTS = len(Inputs)
    NUM_OUTPUTS = 1

    non_integer_scale_factors_error = 'Non-integer scale factors are not supported'

    def __init__(self, name, scale_factors: Sequence, clip_window: Sequence, **kwargs):
        super().__init__(name, **kwargs)
        assert len(scale_factors) == 4, 'Expected 4 scale factors'
        self.scale_factors = tuple(map(float, scale_factors))
        assert len(clip_window) == 4, 'Expected 4 values for clip_window'
        self.clip_window = tuple(map(float, clip_window))

    def _validate(self):
        if USE_OLD_UNI_LAYER and any(int(f) != f for f in self.scale_factors):
            self.raise_op_param_error('scale_factors', self.scale_factors, self.non_integer_scale_factors_error)

    def _export_uni_model_v1(self):
        from uni_model import UniLayerDecode
        assert all(int(f) == f for f in self.scale_factors)
        return UniLayerDecode(self.name,
                              scale_factors=[int(f) for f in self.scale_factors],
                              clipping_list=list(self.clip_window),
                              code_size=0,
                              coordinate_orientation='yxyx',
                              out_dtypes=self.get_uni_model_out_dtypes())

    def _export_uni_model_v2(self):
        from uni_model import UniLayerFasterRCNNBoxDecode
        return UniLayerFasterRCNNBoxDecode(self.name,
                                           scale_factors=list(self.scale_factors),
                                           clipping_window=list(self.clip_window),
                                           out_dtypes=self.get_uni_model_out_dtypes())

    def export_uni_model(self):
        if USE_OLD_UNI_LAYER:
            return self._export_uni_model_v1()
        else:
            return self._export_uni_model_v2()
