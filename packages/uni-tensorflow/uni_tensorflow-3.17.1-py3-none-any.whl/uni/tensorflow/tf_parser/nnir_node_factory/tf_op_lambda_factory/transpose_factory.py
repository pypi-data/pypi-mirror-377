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
Created on 1/5/23

@author: irenab
"""
from uni.common.core.nnir_graph.nnir_nodes import Transpose
from uni.common.core.node_history import NodeHistory
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFTransposeToNnir(TFOpLambdaToNnirFactory):

    @classmethod
    @validate_tf_op_lambda(attrs=['perm'], optional_attrs=['conjugate'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Transpose:
        # tf.transpose has 'conjugate' attr, which only affects complex numbers, so we can ignore it
        history = NodeHistory(cls.tf_op_info(node))
        axes = attrs['perm']
        if axes is None:
            dynamic_input_shapes = cls.get_dynamic_input_shapes(node)
            # If perm is not specified, dims are reversed in tf
            ndims = len(dynamic_input_shapes[0])
            axes = reversed(range(ndims))
        return Transpose(node.name, tuple(axes), history=history)
