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
Created on 12/5/22

@author: irenab
"""
from enum import Enum
import dataclasses


class Framework(str, Enum):
    nnir = 'Internal'    # internal nodes
    onnx = 'ONNX'
    tensorflow = 'TensorFlow'


@dataclasses.dataclass
class OpInfo:
    node_id: str
    op: str
    framework: str

    def clone(self, **kwargs):
        return dataclasses.replace(self, **kwargs)
