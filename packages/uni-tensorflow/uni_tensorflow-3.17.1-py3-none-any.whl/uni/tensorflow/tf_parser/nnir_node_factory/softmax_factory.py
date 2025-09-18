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
Created on 1/1/23

@author: irenab
"""
from uni.common.core.nnir_graph.nnir_nodes import Softmax
from uni.common.core.error import raise_op_param_error
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory, validate_tf


class TFSoftmaxToNnir(TFNodeFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Softmax """

    mask_unsupported_error = 'Mask call argument is not supported'

    @classmethod
    @validate_tf(attrs=['axis'], optional_call_kwargs=['mask'])
    def convert(cls, node: TFMetaNode) -> Softmax:
        axis = node.get_attr('axis')

        mask = cls.tf_reader_helper.get_call_kwargs(node.keras_layer).get('mask')
        if mask is not None:
            raise_op_param_error(cls.tf_op_info(node), 'Call argument: mask', '...', cls.mask_unsupported_error, None)

        return Softmax(node.name, axis=axis)
