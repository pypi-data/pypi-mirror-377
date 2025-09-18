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

from uni.common.core.error import ParamErrorInfo
from uni.common.core.nnir_graph.nnir_nodes import Resize
from uni.tensorflow.tf_parser.nnir_node_factory.resize_factory_base import TFResizeToNnirBase
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode


class TFResizingToNnir(TFResizeToNnirBase):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Resizing """
    unsupported_crop_to_aspect_ratio_error_msg = "crop_to_aspect_ratio is not supported"

    fw_method_attr_name = "interpolation"

    @classmethod
    @validate_tf(attrs=["height", "width", "crop_to_aspect_ratio", fw_method_attr_name])
    def convert(cls, node: TFMetaNode) -> Resize:
        height = node.get_attr("height")
        width = node.get_attr("width")
        size = (height, width)
        method = node.get_attr(cls.fw_method_attr_name)
        crop_to_aspect_ratio = node.get_attr("crop_to_aspect_ratio")
        errors: List[ParamErrorInfo] = []
        if crop_to_aspect_ratio:
            errors.append(
                ParamErrorInfo("crop_to_aspect_ratio", crop_to_aspect_ratio,
                               cls.unsupported_crop_to_aspect_ratio_error_msg))

        return cls.base_convert(node, size, method, errors)
