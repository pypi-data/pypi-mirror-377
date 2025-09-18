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
Created on 1/15/23

@author: irenab
"""
from typing import Tuple, List, Dict, Any

from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Stack
from uni.common.core.node_history import NodeHistory
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.tf_mct_reader_helper import get_quant
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFStackToNnir(TFOpLambdaToNnirFactory):

    @classmethod
    @validate_tf_op_lambda(attrs=[], optional_attrs=['axis'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Stack:
        axis = attrs.get('axis')
        return Stack(node.name, axis=axis, history=NodeHistory(cls.tf_op_info(node)))


class TFQStackToNnir(TFOpLambdaToNnirFactory):

    @classmethod
    @validate_tf_op_lambda(attrs=[], optional_attrs=['axis'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Tuple[Stack, List[GraphRequest]]:
        if hasattr(node.keras_layer, 'axis'):
            axis = node.keras_layer.axis    # type: ignore
        else:
            # default axis for tf.stack is 0
            axis = 0
        nnir_node = Stack(node.name, axis=axis, history=NodeHistory(cls.tf_op_info(node)))
        quantized_weights: Dict[int, Any] = node.keras_layer.quantized_weights    # type: ignore
        idx_list = sorted(list(quantized_weights.keys()))
        assert all(
            isinstance(idx, int)
            for idx in idx_list), f"Error in node: {node.name} quantized_weights expect key to be int got: {idx_list}"
        requests = []
        for index in idx_list:
            data = quantized_weights[index].numpy()
            quant = get_quant(node.keras_layer, str(index))
            requests.append(
                GraphRequest.request_insert_const_as_input(node.name + f'_const{index}',
                                                           data,
                                                           input_index=index,
                                                           validate_const_insert_at_the_end=False,
                                                           quant=quant))
        return nnir_node, requests
