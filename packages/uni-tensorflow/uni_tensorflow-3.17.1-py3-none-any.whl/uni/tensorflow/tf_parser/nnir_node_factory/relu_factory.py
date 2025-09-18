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
from typing import Tuple, Union

import numpy as np

from .tf_node_factory import TFNodeFactory, validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.common.core.nnir_graph.nnir_nodes import ReluX, PRelu
from uni.common.core.node_history import NodeHistory
from uni.common.core.error.defs import ParamErrorInfo
from uni.common.core.error.util import supported_vals_msg, raise_op_error
from uni.common.core.multigraph.node_graph_api import GraphRequest


class TFReluToNnir(TFNodeFactory):
    supported_threshold = 0.
    invalid_threshold_error = supported_vals_msg([supported_threshold])

    invalid_neg_slope_with_max_val = 'Negative slope with max_value is not supported'

    @classmethod
    @validate_tf(attrs=['max_value', 'negative_slope', 'threshold'])
    def convert(cls, node: TFMetaNode) -> Union[ReluX, Tuple[PRelu, GraphRequest]]:
        """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/ReLU """

        max_val = node.get_attr('max_value')
        neg_slope = node.get_attr('negative_slope')
        threshold = node.get_attr('threshold')

        errors = []
        if not np.isclose(threshold, cls.supported_threshold):
            errors.append(
                ParamErrorInfo('threshold', value=node.get_attr('threshold'), reason=cls.invalid_threshold_error))

        if neg_slope and max_val is not None:
            errors.append(
                ParamErrorInfo('negative_slope, max_value',
                               f'{neg_slope}, {max_val}',
                               reason=cls.invalid_neg_slope_with_max_val))

        if errors:
            raise_op_error(cls.tf_op_info(node), errors=errors, history=None)

        if neg_slope:
            history = NodeHistory(op_info=cls.tf_op_info(node), desc='ReLU with negative slope -> PRelU')
            return PRelu(name=node.name, history=history), PRelu.request_add_slope_const(node.name, neg_slope)

        return ReluX(name=node.name, x=max_val, history=NodeHistory(cls.tf_op_info(node), ''))
