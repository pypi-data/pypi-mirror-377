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
Created on 3/13/23

@author: irenab
"""
from uni.common.core.nnir_graph.nnir_nodes import Reshape
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFReshapeToNnir(TFOpLambdaToNnirFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/reshape """

    @classmethod
    @validate_tf_op_lambda(attrs=['shape'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Reshape:
        return Reshape(node.name, target_shape=tuple(attrs['shape']), history=cls.tf_op_history(node))
