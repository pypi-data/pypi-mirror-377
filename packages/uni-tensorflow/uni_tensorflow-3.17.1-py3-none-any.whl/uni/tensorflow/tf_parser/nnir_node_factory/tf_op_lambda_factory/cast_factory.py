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
from typing import List

from uni.common.core.error import ParamErrorInfo, supported_vals_msg, OpInputErrorInfo, raise_op_error, ErrorInfo
from uni.common.core.nnir_graph.nnir_nodes import Identity
from uni.common.core.node_history import NodeHistory
from uni.tensorflow.tf_parser.nnir_node_factory.tf_op_lambda_factory.tf_op_lambda_factory_base import \
    TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
import tensorflow as tf


class TFCastToNnir(TFOpLambdaToNnirFactory):
    """  https://www.tensorflow.org/api_docs/python/tf/cast  """
    supported_src_dtype = tf.bool
    supported_dest_dtype = 'float32'
    src_dtype_err_msg = "Only input of tf.bool is supported"
    dest_dtype_err_msg = supported_vals_msg(supported_dest_dtype)

    @classmethod
    @validate_tf_op_lambda(attrs=['dtype'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Identity:
        dest_dtype = attrs['dtype']
        src_dtype = node.keras_layer.input.dtype    # type: ignore [union-attr]
        errors: List[ErrorInfo] = []
        if src_dtype != cls.supported_src_dtype:
            errors.append(
                OpInputErrorInfo(
                    input_index=0,
                    input_name=node.keras_layer.input.name,    # type: ignore [union-attr]
                    reason=cls.src_dtype_err_msg))
        if dest_dtype != cls.supported_dest_dtype:
            errors.append(ParamErrorInfo('dtype', dest_dtype, cls.dest_dtype_err_msg))

        if errors:
            raise_op_error(cls.tf_op_info(node), errors, history=None)
        history = NodeHistory(cls.tf_op_info(node))
        return Identity(node.name, history=history)
