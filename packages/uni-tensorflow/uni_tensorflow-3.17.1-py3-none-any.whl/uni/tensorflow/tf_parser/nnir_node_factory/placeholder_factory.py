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
Created on 12/12/22

@author: irenab
"""
import numpy as np

from uni.common.core.nnir_graph.semantics import DataFormat
from .tf_node_factory import TFNodeFactory, validate_tf, TFMetaNode
from uni.common.core.nnir_graph.nnir_nodes import Placeholder


class TFPlaceholderToNnir(TFNodeFactory):

    @classmethod
    @validate_tf(attrs=['batch_input_shape', 'dtype', 'sparse', 'ragged'])
    def convert(cls, node: TFMetaNode) -> Placeholder:
        ordinal = node.extra['ordinal']    # type: ignore
        return Placeholder(node.name,
                           shape=node.get_attr('batch_input_shape'),
                           ordinal=ordinal,
                           data_format=DataFormat.HWC,
                           dtype=np.dtype(node.get_attr('dtype')))
