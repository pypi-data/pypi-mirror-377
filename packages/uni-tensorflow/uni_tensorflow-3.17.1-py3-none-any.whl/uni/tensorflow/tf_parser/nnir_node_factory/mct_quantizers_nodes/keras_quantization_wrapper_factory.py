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

from typing import Tuple, Union, List

from mct_quantizers.keras.quantizers import (WeightsPOTInferableQuantizer, WeightsSymmetricInferableQuantizer,
                                             WeightsLUTPOTInferableQuantizer, WeightsLUTSymmetricInferableQuantizer)
from uni.common.core.error import supported_vals_msg
from uni.common.core.common import OpInfo, Framework
from uni.common.core.error import raise_op_error, ParamErrorInfo
from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.tensorflow.tf_parser.nnir_node_factory.mct_quantizers_nodes import TFMctFactoryBase
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.tf_reader import TensorflowReader
import tensorflow as tf
from uni.tensorflow.keras_import_util import TFOpLambda
from uni.tensorflow.tf_parser.tf_reader_helper import get_tf_op_lambda_op

from uni.tensorflow.tf_parser.nnir_node_factory.tf_op_lambda_factory import TFOpLambdaToNnirDispatcher

kl = tf.keras.layers


class TFKerasQuantizationWrapperFactory(TFMctFactoryBase):
    SUPPORTED_LAYERS = {
        kl.Conv2D,
        kl.Conv2DTranspose,
        kl.Dense,
        kl.DepthwiseConv2D,
    }
    SUPPORTED_NUM_BITS = [8, 16]
    err_msg_nbit = supported_vals_msg(SUPPORTED_NUM_BITS)

    @classmethod
    def is_supported_node(cls, node: TFMetaNode) -> bool:
        inner_layer = cls.get_op_inner(node)
        if not cls.is_bin_quant_op(inner_layer):
            return type(cls.get_op_inner(node)) in cls.SUPPORTED_LAYERS
        real_op = get_tf_op_lambda_op(node.keras_layer.layer)    # type: ignore
        return real_op in TFOpLambdaToNnirDispatcher.get_tf_lambda_quant_ops()

    @classmethod
    def is_bin_quant_op(cls, inner_layer):
        return type(inner_layer) is TFOpLambda

    # 'weights_value', 'op_call_args', 'op_call_kwargs', 'is_inputs_as_list' are from MCTQ >= 1.5.0
    # put them in the optional_attrs list to support older versions
    @classmethod
    @validate_tf(attrs=['layer', 'weights_quantizer', 'mctq_version'],
                 optional_attrs=['weights_value', 'op_call_args', 'op_call_kwargs', 'is_inputs_as_list'],
                 skip_call_kwargs=True)
    def convert(cls, node: TFMetaNode) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        layer = cls.get_updated_inner_layer(node)
        tf_op = TensorflowReader.get_tf_op(layer)
        inner_node = node.clone(op=tf_op, keras_layer=layer)
        factory = cls.get_factory(layer)
        return factory.convert(inner_node)

    @classmethod
    def get_factory(cls, layer):
        from uni.tensorflow.tf_parser.tf_op_to_factory import tf_op_factory
        op = type(layer)
        factory = tf_op_factory[op]
        return factory

    @classmethod
    def get_updated_inner_layer(cls, node):
        assert node.keras_layer is not None
        layer = cls.get_op_inner(node)
        # mct_quantizers set attr "get_weights_vars" a list of (attr, tensor, quant)
        # can't read the kernel/bias directly from node.keras_layer.layer because is not updated in training
        # using protected members to reuse the code of factory layers
        errors: List[ParamErrorInfo] = []
        quantized_weights = node.keras_layer.get_quantized_weights()
        is_bin_quant_op = cls.is_bin_quant_op(layer)
        for attr, _, quant in node.keras_layer.get_weights_vars():
            if is_bin_quant_op:
                cls.check_const_quant_supported(attr, quant, errors)
                if quant.channel_axis is not None and quant.channel_axis < 0:
                    quant.channel_axis = quant.channel_axis + quant.input_rank
            else:
                cls.check_quant_supported(attr, quant, errors)
        if errors:
            op_info = cls.keras_quantization_wrapper_tf_op_info(node) if is_bin_quant_op else cls.tf_op_info(node)
            raise_op_error(op_info, errors=errors, history=None)
        if is_bin_quant_op:
            layer.quantized_weights = quantized_weights
            for k, v in node.keras_layer.op_call_kwargs.items():
                if k not in ["name"]:
                    setattr(layer, k, v)
        else:
            for attr, tensor, quant in node.keras_layer.get_weights_vars():
                if attr in quantized_weights:
                    tensor = quantized_weights[attr]
                setattr(layer, attr, tensor)
        # noinspection PyProtectedMember
        layer._name = node.keras_layer._name
        # noinspection PyProtectedMember
        layer._inbound_nodes = node.keras_layer._inbound_nodes
        layer.get_weights_vars = lambda: node.keras_layer.get_weights_vars()
        return layer

    @classmethod
    def get_op_inner(cls, node: TFMetaNode):
        return node.keras_layer.layer    # type: ignore

    @classmethod
    def get_op_inner_name(cls, node: TFMetaNode):
        return cls.get_op_inner(node).__class__.__name__

    @classmethod
    def check_quant_supported(cls, attr, quant, errors):
        if isinstance(quant, (WeightsPOTInferableQuantizer, WeightsSymmetricInferableQuantizer,
                              WeightsLUTPOTInferableQuantizer, WeightsLUTSymmetricInferableQuantizer)):
            return

        name = f"quantized_weights::{attr}"
        value = quant.__class__.__name__
        reason = cls.get_quant_err_msg(value)
        errors.append(ParamErrorInfo(name=name, value=value, reason=reason))

    @classmethod
    def check_const_quant_supported(cls, attr, quant, errors):
        # check is the quant is supported in none conv/matmul layers
        if not isinstance(quant, WeightsPOTInferableQuantizer):
            name = f"quantized_weights::{attr}"
            value = quant.__class__.__name__
            reason = cls.get_quant_err_msg(value, for_this_op=True)
            errors.append(ParamErrorInfo(name=name, value=value, reason=reason))
        else:
            if quant.num_bits not in cls.SUPPORTED_NUM_BITS:
                reason = cls.err_msg_nbit
                errors.append(ParamErrorInfo(name="num_bits", value=quant.num_bits, reason=reason))

    @staticmethod
    def get_quant_err_msg(quant_name, for_this_op=False):
        res = f"Quantization: {quant_name} is not supported"
        if for_this_op:
            res += " for this op"
        return res

    @staticmethod
    def keras_quantization_wrapper_tf_op_info(node: TFMetaNode):
        wrapper_name = node.keras_layer.__class__.__name__
        lambda_name = node.keras_layer.layer.__class__.__name__    # type: ignore[union-attr]
        op_name = get_tf_op_lambda_op(node.keras_layer.layer)    # type: ignore[union-attr]
        op = f"{wrapper_name}::{lambda_name}::{op_name}"
        return OpInfo(node_id=node.name, op=op, framework=Framework.tensorflow)
