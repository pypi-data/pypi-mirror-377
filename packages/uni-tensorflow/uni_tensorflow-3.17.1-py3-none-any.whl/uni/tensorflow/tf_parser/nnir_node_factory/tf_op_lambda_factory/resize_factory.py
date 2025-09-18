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
from uni.tensorflow.tf_parser.nnir_node_factory.tf_op_lambda_factory.tf_op_lambda_factory_base import \
    validate_tf_op_lambda, OpLambdaAttrs
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode


class TFResizeToNnir(TFResizeToNnirBase):
    """ https://www.tensorflow.org/api_docs/python/tf/image/resize """

    unsupported_preserve_aspect_ratio_error_msg = "preserve_aspect_ratio is not supported"
    unsupported_antialias_error_msg = "antialias is not supported"

    fw_method_attr_name = "method"

    @classmethod
    @validate_tf_op_lambda(attrs=["size"], optional_attrs=["preserve_aspect_ratio", "antialias", fw_method_attr_name])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Resize:
        size = attrs["size"]
        method = attrs.get(cls.fw_method_attr_name)
        preserve_aspect_ratio = attrs.get("preserve_aspect_ratio")
        antialias = attrs.get("antialias")
        errors: List[ParamErrorInfo] = []
        if preserve_aspect_ratio:
            errors.append(
                ParamErrorInfo("preserve_aspect_ratio", preserve_aspect_ratio,
                               cls.unsupported_preserve_aspect_ratio_error_msg))
        if antialias:
            errors.append(ParamErrorInfo("antialias", antialias, cls.unsupported_antialias_error_msg))
        return cls.base_convert(node, size, method, errors)
