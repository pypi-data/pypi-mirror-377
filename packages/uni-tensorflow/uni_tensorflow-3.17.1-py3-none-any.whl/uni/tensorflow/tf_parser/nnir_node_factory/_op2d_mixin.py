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
import abc

from uni.common.core.error.util import supported_vals_msg, raise_op_param_error
from uni.common.core.nnir_graph.semantics import DataFormat, SemanticsHelper
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory, TFMetaNode


class TFOp2dMixin(abc.ABC):
    tf_op2d_attrs = ['data_format']

    supported_data_format = ['channels_last']
    data_format_error = supported_vals_msg(supported_data_format)

    data_format = DataFormat.HWC

    @classmethod
    def validate_data_format(cls, tf_node: TFMetaNode):
        """ Validate data_format attribute
            Raises:
                InvalidOpError
                """
        data_format = tf_node.get_attr('data_format')
        if data_format in cls.supported_data_format:
            return

        op_info = TFNodeFactory.tf_op_info(tf_node)
        raise_op_param_error(op_info, 'data_format', data_format, reason=cls.data_format_error, history=None)

    @classmethod
    def get_hw_axes(cls):
        helper = SemanticsHelper(cls.data_format)
        h = helper.data_h_axis()
        w = helper.data_w_axis()
        return h, w

    @classmethod
    def get_hw(cls, shape: tuple):
        assert len(shape) == 4
        h, w = cls.get_hw_axes()
        return shape[h], shape[w]
