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


class Squeeze(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    def __init__(self, name, squeeze_dims: List[int], **kwargs):
        super().__init__(name, **kwargs)
        self.squeeze_dims = squeeze_dims

    def export_uni_model(self):
        from uni_model import UniLayerSqueeze
        return UniLayerSqueeze(self.name,
                               squeeze_dims=[int(v) for v in self.squeeze_dims],
                               out_dtypes=self.get_uni_model_out_dtypes())
