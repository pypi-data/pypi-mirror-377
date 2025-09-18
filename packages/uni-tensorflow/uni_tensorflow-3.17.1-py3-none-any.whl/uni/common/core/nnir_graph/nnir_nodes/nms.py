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
Created on 8/27/23

@author: irenab
"""
from typing import List    # noqa: F401
from enum import IntEnum

from .nnir_node import NnirNode
from uni.common.core.error import raise_op_error, OpInputErrorInfo, ParamErrorInfo, exceeds_limit_msg
from uni.common.core.error import ErrorInfo    # noqa: F401


class Inputs(IntEnum):
    Boxes = 0
    Scores = 1


class Outputs(IntEnum):
    Boxes = 0
    Scores = 1
    Labels = 2
    Indices = 3
    ValidDetections = 4


class ScoreDims(IntEnum):
    Boxes = -2
    Labels = -1


class MultiClassNonMaxSuppression(NnirNode):
    Inputs = Inputs
    Outputs = Outputs

    NUM_INPUTS = len(Inputs)
    NUM_OUTPUTS = [len(Outputs) - 1, len(Outputs)]    # see NMSOutputsSubstitution
    WITH_INDICES = False

    max_num_classes = 1000
    max_num_scores = 2097120    # 32*(64*1024-1)
    max_num_detections = 500
    invalid_num_classes = exceeds_limit_msg('#classes', max_num_classes)
    invalid_num_scores = exceeds_limit_msg('#boxes X #classes', max_num_scores)
    invalid_num_detections = exceeds_limit_msg('#output detections', max_num_detections)
    invalid_score_threshold = 'negative score threshold is not supported'

    def __init__(self, name, score_threshold: float, iou_threshold: float, max_detections: int, **kwargs):
        super().__init__(name, **kwargs)
        self.score_threshold = score_threshold
        self.iou_threshold = iou_threshold
        self.max_detections = max_detections

    def _validate(self):
        errors = []    # type: List[ErrorInfo]
        if self.max_detections > self.max_num_detections:
            errors.append(ParamErrorInfo('max_detections', self.max_detections, self.invalid_num_detections))

        if self.score_threshold < 0:
            errors.append(ParamErrorInfo('score_threshold', self.score_threshold, self.invalid_score_threshold))

        score_shape = self.graph_ctx.get_in_shapes()[Inputs.Scores]
        n_classes = score_shape[ScoreDims.Labels]
        n_boxes = score_shape[ScoreDims.Boxes]
        if n_classes > self.max_num_classes:
            errors.append(OpInputErrorInfo(Inputs.Scores, 'scores', reason=self.invalid_num_classes))
        if n_boxes * n_classes > self.max_num_scores:
            errors.append(OpInputErrorInfo(Inputs.Scores, 'scores', reason=self.invalid_num_scores))
        if errors:
            raise_op_error(self.op_info(), errors, self.history)

    def get_uni_model_num_outputs(self):
        return len(self.Outputs)

    def export_uni_model(self):
        from uni_model import UniLayerMultiClassNonMaxSuppression
        return UniLayerMultiClassNonMaxSuppression(self.name,
                                                   score_threshold=self.score_threshold,
                                                   iou_threshold=self.iou_threshold,
                                                   max_detections=self.max_detections,
                                                   out_dtypes=self.get_uni_model_out_dtypes())
