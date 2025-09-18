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
Created on 1/15/23

@author: irenab
"""
from uni.common.core.nnir_graph.nnir_nodes import Matmul
from uni.common.core.error.util import raise_op_error, ParamErrorInfo
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFMatmulToNnir(TFOpLambdaToNnirFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/linalg/matmul """

    unsupported_param = 'Unsupported parameter'
    _optional_attrs = [
        'transpose_a', 'transpose_b', 'adjoint_a', 'adjoint_b', 'a_is_sparse', 'b_is_sparse', 'output_type'
    ]

    @classmethod
    @validate_tf_op_lambda(attrs=['b'], optional_attrs=_optional_attrs)
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Matmul:
        transpose_a = attrs.get('transpose_a')
        transpose_b = attrs.get('transpose_b')

        errors = []
        # tf matmul also has *_is_sparse flag, but it only allows more efficient tf implementation to be used,
        # so we don't care about it
        for key in ['adjoint_a', 'adjoint_b']:
            val = attrs.get(key)
            if val:
                errors.append(ParamErrorInfo(name=key, value=val, reason=cls.unsupported_param))
        if errors:
            raise_op_error(cls.tf_op_info(node), errors=errors, history=None)

        return Matmul(node.name, transpose_a=transpose_a, transpose_b=transpose_b)
