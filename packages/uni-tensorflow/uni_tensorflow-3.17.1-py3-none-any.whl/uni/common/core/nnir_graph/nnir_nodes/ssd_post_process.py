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
import dataclasses
from typing import Tuple, List, Dict    # noqa: F401
from enum import Enum, auto, IntEnum

from uni.common.core.nnir_graph.nnir_edge import NnirEdge
from uni.common.core.node_history import NodeHistory
from . import NnirNode, FasterRCNNBoxDecode, MultiClassNonMaxSuppression, Reshape, Slice, Softmax, Sigmoid


class ScoreConverter(Enum):
    Sigmoid = auto()
    Softmax = auto()
    Linear = auto()


class Inputs(IntEnum):
    Offsets = 0
    Scores = 1
    Anchors = 2


class SSDPostProcess(NnirNode):
    Inputs = Inputs
    Outputs = MultiClassNonMaxSuppression.Outputs

    NUM_INPUTS = len(Inputs)
    NUM_OUTPUTS = [len(MultiClassNonMaxSuppression.Outputs) - 1,
                   len(MultiClassNonMaxSuppression.Outputs)]    # see NMSOutputsSubstitution

    def __init__(self,
                 name,
                 scale_factors: Tuple[float, ...],
                 clip_size: Tuple[float, ...],
                 score_converter: ScoreConverter,
                 score_threshold: float,
                 iou_threshold: float,
                 max_detections: int,
                 remove_background: bool,
                 **kwargs):    # yapf: disable
        super().__init__(name, **kwargs)
        self.scale_factors = scale_factors
        self.clip_size = clip_size
        self.score_converter = score_converter
        self.score_threshold = score_threshold
        self.iou_threshold = iou_threshold
        self.max_detections = max_detections
        self.remove_background = remove_background

    def _validate(self):
        # we require all outputs to be last
        self.validate_node_output_is_network_output()

    def export_uni_model(self):
        raise RuntimeError(f'{self.op} is not expected to be exported directly')

    def substitute(self) -> Tuple[List[NnirNode], List['NnirEdge']]:
        """
        offsets scores anchors              offsets  anchors          scores
             |    |     |        =====>        |        |               |
            SSDPostProcess                 FasterRCNNBoxDecode    Sigmoid/Softmax (optional)
                                                    |                   |
                                                 Reshape           Slice (optional)
                                                    |                   |
                                                 MultiClassNonMaxSuppression
        """

        input_edges = self.graph_ctx.get_in_edges()    # type: List[NnirEdge]
        input_box_edge = input_edges[self.Inputs.Offsets]
        input_score_edge = input_edges[self.Inputs.Scores]
        input_anchors_edge = input_edges[self.Inputs.Anchors]
        out_edges = self.graph_ctx.get_out_edges()    # type: Dict[int, List[NnirEdge]]

        nodes: List[NnirNode] = []
        edges: List[NnirEdge] = []
        history = NodeHistory(self.op_info(), desc=f'{self.op} replacer')

        # add box decode
        box_decode = FasterRCNNBoxDecode(self.name + '/BoxDecode',
                                         self.scale_factors, (0, 0, *self.clip_size),
                                         history=history)
        nodes.append(box_decode)
        edges.extend([
            input_box_edge.clone(dest=box_decode.name, dest_index=FasterRCNNBoxDecode.Inputs.Offsets),
            input_anchors_edge.clone(dest=box_decode.name, dest_index=FasterRCNNBoxDecode.Inputs.Anchors)
        ])
        assert input_box_edge.shape is not None
        target_shape = (*input_box_edge.shape[:-1], 1, input_box_edge.shape[-1])
        reshape = Reshape(self.name + '/Reshape', target_shape=target_shape)
        nodes.append(reshape)
        edges.append(
            NnirEdge(src=box_decode.name, src_index=0, dest=reshape.name, dest_index=0, shape=input_box_edge.shape))
        nms_box_src_info = SrcInfo(reshape.name, 0, target_shape)

        # add optional scores converter and background slicer
        nms_score_src_info = self._add_score_nodes(input_score_edge, history, nodes, edges)

        # add nms
        nms = self._add_nms(nms_box_src_info, nms_score_src_info, history, nodes, edges)

        # if outputs order diverge for some reason need to map the outputs
        assert self.Outputs == nms.Outputs
        edges.extend([e.clone(src=nms.name) for v in out_edges.values() for e in v])
        return nodes, edges

    def _add_score_nodes(self, input_score_edge, history, nodes, edges) -> 'SrcInfo':
        # add score converter
        factory = {
            ScoreConverter.Linear: lambda: None,
            ScoreConverter.Sigmoid: lambda: Sigmoid(self.name + '/Sigmoid', history=history),
            ScoreConverter.Softmax: lambda: Softmax(self.name + '/Softmax', axis=-1, history=history),
        }

        score_src_info = SrcInfo(input_score_edge.src, input_score_edge.src_index, input_score_edge.shape)
        score_conv = factory[self.score_converter]()
        if score_conv is not None:
            nodes.append(score_conv)
            edges.append(input_score_edge.clone(dest=score_conv.name, dest_index=0))
            score_src_info.name = score_conv.name
            score_src_info.index = 0

        # add slice
        if self.remove_background:
            slice_bg = Slice(self.name + '/Slice', begin=[0, 0, 1], size=[-1, -1, -1], history=history)
            nodes.append(slice_bg)
            edges.append(
                NnirEdge(src=score_src_info.name,
                         src_index=score_src_info.index,
                         dest=slice_bg.name,
                         dest_index=0,
                         shape=input_score_edge.shape))
            score_src_info.name = slice_bg.name
            score_src_info.index = 0
            score_src_info.shape = (*input_score_edge.shape[:-1], input_score_edge.shape[-1] - 1)

        return score_src_info

    def _add_nms(self, box_src_info: 'SrcInfo', score_src_info: 'SrcInfo', history, nodes,
                 edges) -> MultiClassNonMaxSuppression:
        nms = MultiClassNonMaxSuppression(self.name + '/NMS',
                                          score_threshold=self.score_threshold,
                                          iou_threshold=self.iou_threshold,
                                          max_detections=self.max_detections,
                                          history=history)
        nodes.append(nms)

        edges.extend([
            NnirEdge(src=box_src_info.name,
                     src_index=box_src_info.index,
                     dest=nms.name,
                     dest_index=nms.Inputs.Boxes,
                     shape=box_src_info.shape),
            NnirEdge(src=score_src_info.name,
                     src_index=score_src_info.index,
                     dest=nms.name,
                     dest_index=nms.Inputs.Scores,
                     shape=score_src_info.shape)
        ])
        return nms

    def get_uni_model_num_outputs(self):
        return len(self.Outputs)


@dataclasses.dataclass
class SrcInfo:
    name: str
    index: int
    shape: tuple
