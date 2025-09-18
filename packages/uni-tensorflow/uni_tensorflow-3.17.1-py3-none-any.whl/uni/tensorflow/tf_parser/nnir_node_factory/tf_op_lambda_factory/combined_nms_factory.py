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
Created on 9/13/23

@author: irenab
"""
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.common.core.nnir_graph.nnir_nodes import MultiClassNonMaxSuppression
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs
from uni.common.core.error import ParamErrorInfo, raise_op_error


class TFCombinedNMSToNnir(TFOpLambdaToNnirFactory):
    invalid_size_per_class = 'max_output_size_per_class must be equal to max_total_size'
    invalid_clip = 'box clipping is not supported'
    invalid_pad_per_class = 'padding per class is not supported'

    @classmethod
    @validate_tf_op_lambda(attrs=['scores', 'max_output_size_per_class', 'max_total_size'],
                           optional_attrs=['iou_threshold', 'score_threshold', 'pad_per_class', 'clip_boxes'])
    def convert(cls, tf_node: TFMetaNode, attrs: OpLambdaAttrs) -> MultiClassNonMaxSuppression:
        """ https://www.tensorflow.org/api_docs/python/tf/image/combined_non_max_suppression """

        errors = []

        max_detections = attrs['max_total_size']
        max_size_per_class = attrs['max_output_size_per_class']
        if max_size_per_class != max_detections:
            errors.append(ParamErrorInfo('max_output_size_per_class', max_size_per_class, cls.invalid_size_per_class))

        if attrs.get('clip_boxes'):
            errors.append(ParamErrorInfo('clip_boxes', attrs.get('clip_boxes'), cls.invalid_clip))

        if attrs.get('pad_per_class'):
            errors.append(ParamErrorInfo('pad_per_class', attrs.get('pad_per_class'), cls.invalid_pad_per_class))

        score_threshold = attrs.get('score_threshold')

        if errors:
            raise_op_error(cls.tf_op_info(tf_node), errors, None)

        return MultiClassNonMaxSuppression(tf_node.name,
                                           score_threshold=score_threshold,
                                           iou_threshold=attrs.get('iou_threshold'),
                                           max_detections=max_detections)
