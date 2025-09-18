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
Created on 3/16/23

@author: irenab
"""
import abc
from typing import Type

from uni.common.core.nnir_graph.nnir_nodes import ReduceMean, ReduceMax, ReduceSum
from uni.common.core.nnir_graph.nnir_nodes.reduce_ops import ReduceNodeBase
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFReduceOpToNnirBase(TFOpLambdaToNnirFactory, abc.ABC):
    nnir_op: Type

    @classmethod
    @validate_tf_op_lambda(attrs=[], optional_attrs=['axis', 'keepdims'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> ReduceNodeBase:
        axes = attrs.get('axis')
        if axes is None:
            dynamic_input_shapes = cls.get_dynamic_input_shapes(node)
            axes = tuple(range(len(dynamic_input_shapes[0])))
        keepdims = attrs.get('keepdims')
        return cls.nnir_op(node.name, axes=axes, keepdims=keepdims)


class TFReduceMeanToNnir(TFReduceOpToNnirBase):
    """ https://www.tensorflow.org/api_docs/python/tf/math/reduce_mean """
    nnir_op = ReduceMean


class TFReduceMaxToNnir(TFReduceOpToNnirBase):
    """ https://www.tensorflow.org/api_docs/python/tf/math/reduce_max """
    nnir_op = ReduceMax


class TFReduceSumToNnir(TFReduceOpToNnirBase):
    """ https://www.tensorflow.org/api_docs/python/tf/math/reduce_sum """
    nnir_op = ReduceSum
