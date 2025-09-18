# -------------------------------------------------------------------------------
# (c) Copyright 2022 Sony Semiconductor Israel, Ltd. All rights reserved.
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
Created on 12/12/22

@author: irenab
"""
from typing import Tuple, Union, Set

from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory, validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.tf_reader_helper import get_tf_op_lambda_op, get_tf_op_lambda_attrs
from .broadcast_to_factory import TFBroadcastToToNnir
from .gelu import TFGeluToNnir
from .negative_factory import TFNegativeToNnir
from .norm_factory import TFNormToNnir
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, OpLambdaAttrs
from .abs_factory import TFAbsToNnir
from .argmax_factory import TFArgmaxToNnir
from .binary_op_factory import TFAddToNnir, TFMulToNnir, TFSubToNnir, TFTruedivToNnir, TFEqualToNnir
from .binary_op_factory import TFQAddToNnir, TFQSubToNnir, TFQMulToNnir, TFQTruedivToNnir
from .cast_factory import TFCastToNnir
from .concat_factory import TFConcatToNnir, TFQConcatToNnir
from .expand_dims_factory import TFExpandDimsToNnir
from .gather_factory import TFGatherToNnir, TFQGatherToNnir
from .identity_factory import TFIdentityToNnir
from .matmul_factory import TFMatmulToNnir
from .pad_factory import TFPadToNnir
from .reduce_factories import TFReduceMeanToNnir, TFReduceMaxToNnir, TFReduceSumToNnir
from .relu import TFReluToNnir
from .relu6 import TFRelu6ToNnir
from .reshape_factory import TFReshapeToNnir
from .resize_factory import TFResizeToNnir
from .rsqrt_factory import TFRSqrtToNnir
from .sigmoid_factory import TFSigmoidToNnir
from .silu_factory import TFSiluToNnir
from .slice_factory import TFSliceToNnir
from .softmax_factory import TFSoftmaxToNnir
from .split_factory import TFSplitToNnir
from .squeeze_factory import TFSqueezeToNnir
from .sqrt_factory import TFSqrtToNnir
from .stack_factory import TFStackToNnir, TFQStackToNnir
from .strided_slice_factory import TFStridedSliceToNnir
from .tanh_factory import TFTanHToNnir
from .top_k_factory import TFTopKToNnir
from .transpose_factory import TFTransposeToNnir
from .unstack_factory import TFUnstackToNnir
from .combined_nms_factory import TFCombinedNMSToNnir


class TFOpLambdaToNnirDispatcher(TFNodeFactory):
    dispatcher = {
        'broadcast_to': TFBroadcastToToNnir,
        'cast': TFCastToNnir,
        'compat.v1.pad': TFPadToNnir,
        'compat.v1.gather': TFGatherToNnir,
        'compat.v1.transpose': TFTransposeToNnir,
        'compat.v1.norm': TFNormToNnir,
        'concat': TFConcatToNnir,
        'expand_dims': TFExpandDimsToNnir,
        'image.combined_non_max_suppression': TFCombinedNMSToNnir,
        'image.resize': TFResizeToNnir,
        'linalg.matmul': TFMatmulToNnir,
        'math.abs': TFAbsToNnir,
        'math.add': TFAddToNnir,    # tf.math.add
        'math.argmax': TFArgmaxToNnir,    # tf.math.argmax
        'math.divide': TFTruedivToNnir,    # tf.math.divide with name!=None
        'math.equal': TFEqualToNnir,    # tf.math.equal
        'math.multiply': TFMulToNnir,    # tf.math.multiply, *
        'math.negative': TFNegativeToNnir,    # tf.math.negative
        'math.reduce_max': TFReduceMaxToNnir,
        'math.reduce_mean': TFReduceMeanToNnir,
        'math.reduce_sum': TFReduceSumToNnir,
        'math.rsqrt': TFRSqrtToNnir,
        'math.sigmoid': TFSigmoidToNnir,
        'math.sqrt': TFSqrtToNnir,
        'math.subtract': TFSubToNnir,    # tf.math.subtract, -
        'math.tanh': TFTanHToNnir,
        'math.top_k': TFTopKToNnir,
        'math.truediv': TFTruedivToNnir,    # tf.math.truediv, tf.math.divide, /
        '__operators__.add': TFAddToNnir,    # +
        'nn.gelu': TFGeluToNnir,
        'nn.relu': TFReluToNnir,
        'nn.relu6': TFRelu6ToNnir,
        'nn.silu': TFSiluToNnir,
        'nn.softmax': TFSoftmaxToNnir,
        'identity': TFIdentityToNnir,
        'reshape': TFReshapeToNnir,
        'slice': TFSliceToNnir,
        'split': TFSplitToNnir,
        'compat.v1.squeeze': TFSqueezeToNnir,
        'stack': TFStackToNnir,
        'strided_slice': TFStridedSliceToNnir,
        'unstack': TFUnstackToNnir,
    }
    q_dispatcher = {
        'concat': TFQConcatToNnir,
        'compat.v1.gather': TFQGatherToNnir,
        'gather': TFQGatherToNnir,
        'math.add': TFQAddToNnir,
        'math.divide': TFQTruedivToNnir,
        'math.multiply': TFQMulToNnir,
        'math.subtract': TFQSubToNnir,
        'math.truediv': TFQTruedivToNnir,
        'stack': TFQStackToNnir,
    }
    invalid_op_error = 'Unsupported tensorflow op (wrapped by TFOpLambda)'

    @classmethod
    def is_supported_node(cls, node: TFMetaNode) -> bool:
        op = get_tf_op_lambda_op(node.keras_layer)
        return op in cls.dispatcher

    @classmethod
    @validate_tf(attrs=['function'], skip_call_kwargs=True)
    def convert(cls, node: TFMetaNode) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        op = get_tf_op_lambda_op(node.keras_layer)
        # factory can contain op: None for earlier validation, but it shouldn't be converted
        if hasattr(node.keras_layer, "quantized_weights"):
            factory = cls.q_dispatcher.get(op)
        else:
            factory = cls.dispatcher.get(op)    # type: ignore
        assert factory is not None, f'Attempted to convert unexpected {op}'
        # make sure tf validation decorator was set
        assert hasattr(factory.convert, 'valid'), node.op

        call_args, call_kwargs, defaults_getter = get_tf_op_lambda_attrs(node.keras_layer)
        op_lambda_attrs = OpLambdaAttrs(call_args, call_kwargs, defaults_getter)
        return factory.convert(node, op_lambda_attrs)

    @staticmethod
    def tf_op_info(node: TFMetaNode):
        return TFOpLambdaToNnirFactory.tf_op_info(node)

    @classmethod
    def get_tf_lambda_quant_ops(cls) -> Set[str]:
        return set(cls.q_dispatcher.keys())
