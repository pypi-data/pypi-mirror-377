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
Created on 12/29/22

@author: irenab
"""
import numpy as np

from .tf_node_factory import TFNodeFactory, validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.common.core.nnir_graph.nnir_nodes import Pad
from uni.common.core.node_history import NodeHistory
from ._op2d_mixin import TFOp2dMixin


class TFZeroPadding2DToNnir(TFNodeFactory, TFOp2dMixin):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/ZeroPadding2D """

    @classmethod
    @validate_tf(attrs=['padding'] + TFOp2dMixin.tf_op2d_attrs)
    def convert(cls, node: TFMetaNode) -> Pad:

        cls.validate_data_format(node)

        padding = node.get_attr('padding')
        pad = np.zeros((4, 2))
        h, w = cls.get_hw_axes()
        pad[h, :] = padding[0]
        pad[w, :] = padding[1]

        history = NodeHistory(cls.tf_op_info(node), desc=f'{node.tf_op_short_name()} -> {Pad.__name__}')
        return Pad(node.name, paddings=pad, pad_const=0., history=history)
