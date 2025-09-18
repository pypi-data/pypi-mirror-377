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
from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.nnir_graph.quant_info.quant_info_base import QuantInfoBase


class Quant(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    def __init__(self, name, quant_info: QuantInfoBase, **kwargs):
        super().__init__(name, **kwargs)
        self.quant_info = quant_info

    def export_uni_model(self):
        raise RuntimeError('Not expected to be called')

    def to_quant_info(self):
        return self.quant_info
