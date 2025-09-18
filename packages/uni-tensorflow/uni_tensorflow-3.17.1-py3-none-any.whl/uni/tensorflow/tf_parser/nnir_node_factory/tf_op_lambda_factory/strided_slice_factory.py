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
Created on 1/16/23

@author: irenab
"""
from uni.common.core.nnir_graph.nnir_nodes import StridedSlice
from uni.common.core.error import ParamErrorInfo, raise_op_error
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFStridedSliceToNnir(TFOpLambdaToNnirFactory):

    unsupported_mask_type = 'Mask type is not supported'
    _unsupported_masks = ['ellipsis_mask', 'new_axis_mask', 'shrink_axis_mask']

    @classmethod
    @validate_tf_op_lambda(attrs=['begin', 'end'],
                           optional_attrs=['strides', 'begin_mask', 'end_mask'] + _unsupported_masks + ['var'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> StridedSlice:
        errors = []
        for mask in cls._unsupported_masks:
            if attrs.get(mask):
                errors.append(ParamErrorInfo(mask, attrs[mask], cls.unsupported_mask_type))
        if errors:
            raise_op_error(cls.tf_op_info(node), errors, history=None)

        begin = attrs['begin']
        end = attrs['end']

        strides = attrs.get('strides')
        # tf default is None since ndims is not known
        if strides is None:
            dynamic_input_shapes = cls.get_dynamic_input_shapes(node)
            strides = [1] * len(dynamic_input_shapes[0])

        begin_mask = attrs.get('begin_mask')
        end_mask = attrs.get('end_mask')
        return StridedSlice(node.name, begin=begin, end=end, strides=strides, begin_mask=begin_mask, end_mask=end_mask)
