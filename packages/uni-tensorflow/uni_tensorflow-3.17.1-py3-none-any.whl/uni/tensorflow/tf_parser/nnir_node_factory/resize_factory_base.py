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
from abc import ABC
from typing import Optional, List
import tensorflow as tf

from uni.common.core.error import ParamErrorInfo, raise_op_error
from uni.common.core.nnir_graph.nnir_nodes import Resize
from uni.common.core.nnir_graph.nnir_nodes.resize import ResizeMode
from uni.tensorflow.tf_parser.nnir_node_factory._op2d_mixin import TFOp2dMixin
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode

TFResizeMethod = tf.image.ResizeMethod


class TFResizeToNnirBase(TFNodeFactory, TFOp2dMixin, ABC):

    fw_method_attr_name: str

    supported_methods = [TFResizeMethod.BILINEAR, TFResizeMethod.NEAREST_NEIGHBOR]
    unsupported_method_error_msg = "Method is not supported"

    @classmethod
    def base_convert(cls, node: TFMetaNode, size, method_str: str, errors: List[ParamErrorInfo]) -> Resize:
        method = cls._get_method(method_str, errors)

        if errors:
            raise_op_error(cls.tf_op_info(node), errors, history=None)
        assert method is not None
        res = Resize(node.name, size[0], size[1], method, history=cls.get_history(node, f'{node.op} -> Resize'))
        res.data_format = cls.data_format
        return res

    @classmethod
    def _get_method(cls, method_str: str, errors) -> Optional[ResizeMode]:
        if method_str not in cls.supported_methods:
            errors.append(ParamErrorInfo(cls.fw_method_attr_name, method_str, cls.unsupported_method_error_msg))
            return None
        if method_str == TFResizeMethod.BILINEAR:
            return ResizeMode.BILINEAR
        if method_str == TFResizeMethod.NEAREST_NEIGHBOR:
            return ResizeMode.NEAREST

        raise ValueError(f"Unknown resize method: {method_str}")
