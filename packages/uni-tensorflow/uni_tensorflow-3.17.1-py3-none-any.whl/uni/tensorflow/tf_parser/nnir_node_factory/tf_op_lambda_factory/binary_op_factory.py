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
Created on 12/19/22

@author: irenab
"""
from typing import Tuple, Type, Optional, Dict, Any
import abc

import numpy as np
from uni.tensorflow.keras_import_util import KerasTensor

from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Add, Div, Mul, Sub, Equal
from uni.common.core.node_history import NodeHistory
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
import uni.tensorflow.tf_parser.tf_mct_reader_helper
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFBinaryOpToNnir(TFOpLambdaToNnirFactory, abc.ABC):
    nnir_op: Type[NnirNode]

    @classmethod
    @validate_tf_op_lambda(attrs=['y'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Tuple[NnirNode, Optional[GraphRequest]]:
        nnir_node = cls.nnir_op(node.name, history=NodeHistory(cls.tf_op_info(node)))
        request = None
        # y always refers to the second input. If it's dynamic it will be KerasTensor
        # If first input is static, y will contain same KerasTensor as inbound_node.keras_inputs, and
        # inbound_node.inputs_tensors contain the first input - dynamic or static
        y = attrs['y']
        if isinstance(y, KerasTensor):
            dynamic_inputs = cls.get_dynamic_inputs(node)
            if len(dynamic_inputs) == 1 and y.name == dynamic_inputs[0].name:
                x = attrs.call_args[0]
                request = GraphRequest.request_insert_const_as_input(node.name + '_x',
                                                                     np.asarray(x),
                                                                     input_index=0,
                                                                     validate_const_insert_at_the_end=False)
        else:
            request = GraphRequest.request_insert_const_as_input(node.name + '_y', np.asarray(y), input_index=1)

        return nnir_node, request


class TFQBinaryOpToNnir(TFOpLambdaToNnirFactory, abc.ABC):
    nnir_op: Type[NnirNode]

    @classmethod
    @validate_tf_op_lambda(attrs=[])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Tuple[NnirNode, Optional[GraphRequest]]:
        nnir_node = cls.nnir_op(node.name, history=NodeHistory(cls.tf_op_info(node)))

        quantized_weights: Dict[int, Any] = node.keras_layer.quantized_weights    # type: ignore

        assert len(quantized_weights) == 1, f"Error in node: {node.name} expect only one key got: {quantized_weights}"
        index = list(quantized_weights.keys())[0]
        # both are assert because this should fail in fw inference
        assert index in [0, 1], f"Error in node: {node.name} quantized_weights expect key [0, 1] got: {index}"
        data = quantized_weights[index].numpy()
        quant = uni.tensorflow.tf_parser.tf_mct_reader_helper.get_quant(node.keras_layer, str(index))
        request = GraphRequest.request_insert_const_as_input(node.name + f'_const{index}',
                                                             data,
                                                             input_index=index,
                                                             validate_const_insert_at_the_end=index == 1,
                                                             quant=quant)
        return nnir_node, request


class TFAddToNnir(TFBinaryOpToNnir):
    """ https://www.tensorflow.org/api_docs/python/tf/math/add
        and operator + """
    nnir_op = Add


class TFQAddToNnir(TFQBinaryOpToNnir):
    nnir_op = Add


class TFTruedivToNnir(TFBinaryOpToNnir):
    """ https://www.tensorflow.org/api_docs/python/tf/math/truediv
        https://www.tensorflow.org/api_docs/python/tf/math/divide
        and operator / """
    nnir_op = Div


class TFQTruedivToNnir(TFQBinaryOpToNnir):
    nnir_op = Div


class TFMulToNnir(TFBinaryOpToNnir):
    """ https://www.tensorflow.org/api_docs/python/tf/math/multiply
        and operator * """
    nnir_op = Mul


class TFQMulToNnir(TFQBinaryOpToNnir):
    nnir_op = Mul


class TFSubToNnir(TFBinaryOpToNnir):
    """ https://www.tensorflow.org/api_docs/python/tf/math/subtract
        and operator - """
    nnir_op = Sub


class TFQSubToNnir(TFQBinaryOpToNnir):
    nnir_op = Sub


class TFEqualToNnir(TFBinaryOpToNnir):
    """ https://www.tensorflow.org/api_docs/python/tf/math/equal
        about operator == look at https://github.com/keras-team/keras/issues/18371 """
    nnir_op = Equal
