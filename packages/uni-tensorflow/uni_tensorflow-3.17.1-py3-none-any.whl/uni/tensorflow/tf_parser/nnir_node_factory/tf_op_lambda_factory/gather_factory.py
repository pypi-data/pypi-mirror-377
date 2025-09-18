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
from typing import List, Tuple, Optional, Any, Dict

import numpy as np
import tensorflow as tf
from uni.common.core.error import ParamErrorInfo, OpInputErrorInfo, raise_op_error, ErrorInfo
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import TopKGather
from uni.tensorflow.keras_import_util import KerasTensor
from uni.tensorflow.tf_parser.nnir_node_factory.tf_op_lambda_factory.tf_op_lambda_factory_base import \
    TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs
from uni.tensorflow.tf_parser.tf_mct_reader_helper import get_quant
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.tf_reader_helper import get_input, get_shape, get_inbound_layers, get_rank, \
    get_dynamic_inputs


class TFGatherToNnir(TFOpLambdaToNnirFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/gather """

    indices_dtype_err_msg = "The dtype of indices must be tf.int32"
    axis_batch_dims_err_msg = "The axis must be equal to batch_dims and must be set to the last axis of the tensor."

    @classmethod
    @validate_tf_op_lambda(attrs=['indices'], optional_attrs=["validate_indices", "axis", "batch_dims"])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Tuple[TopKGather, Optional[GraphRequest]]:
        indices = attrs['indices']
        indices_is_const = not isinstance(indices, KerasTensor)
        if indices_is_const:
            indices = tf.constant(indices)

        assert node.inbound_node_index is not None

        axis = attrs.get("axis")
        batch_dims = attrs.get("batch_dims")

        data_const, data_is_const, params_rank = cls._get_const(indices_is_const, node)
        cls.validate(axis, batch_dims, indices, node, params_rank)

        if data_is_const:
            request = GraphRequest.request_insert_const_as_input(node.name + 'data',
                                                                 data_const,
                                                                 input_index=0,
                                                                 validate_const_insert_at_the_end=False)
        elif indices_is_const:
            request = GraphRequest.request_insert_const_as_input(node.name + 'indices',
                                                                 indices.numpy(),
                                                                 input_index=1,
                                                                 validate_const_insert_at_the_end=True)
        else:
            request = None

        return TopKGather(node.name, axis, history=cls.tf_op_history(node)), request

    @classmethod
    def validate(cls, axis, batch_dims, indices, node, params_rank):
        errors: List[ErrorInfo] = []
        last_axis = params_rank - 1
        supported_axes = [-1, last_axis]
        if indices.dtype != tf.int32:
            errors.append(OpInputErrorInfo(input_index=1, input_name='indices', reason=cls.indices_dtype_err_msg))
        if axis is None and last_axis == 0:
            axis = 0
        if axis not in supported_axes:
            errors.append(ParamErrorInfo(name="axis", value=axis, reason=cls.axis_batch_dims_err_msg))
        if batch_dims not in supported_axes:
            errors.append(ParamErrorInfo(name="batch_dims", value=batch_dims, reason=cls.axis_batch_dims_err_msg))
        if errors:
            raise_op_error(cls.tf_op_info(node), errors=errors, history=cls.tf_op_history(node))

    @classmethod
    def _get_const(cls, indices_is_const, node):
        params_inbound_layer = get_inbound_layers(node.keras_layer, node.inbound_node_index)
        if isinstance(params_inbound_layer, list) or indices_is_const:
            data_is_const = False
            node_input = get_input(node.keras_layer)
            params_rank = get_rank(node_input)
            data_const = None
        else:
            data_is_const = True
            params_in_shape = get_shape(get_input(params_inbound_layer))
            params_rank = len(params_in_shape)
            node_input = get_input(node.keras_layer)
            data_const = np.array(node_input).reshape(params_in_shape)
        return data_const, data_is_const, params_rank


class TFQGatherToNnir(TFOpLambdaToNnirFactory):

    @classmethod
    @validate_tf_op_lambda(attrs=[], optional_attrs=['validate_indices', 'axis', 'batch_dims'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Tuple[TopKGather, GraphRequest]:
        quantized_weights: Dict[int, Any] = node.keras_layer.quantized_weights    # type: ignore
        assert len(quantized_weights) == 1, (f"Error in node: {node.name} quantized_weights"
                                             f" expect only one const got: {len(quantized_weights)}")
        if hasattr(node.keras_layer, 'axis'):
            axis = node.keras_layer.axis    # type: ignore
        else:
            # default value in tensorflow is None
            axis = None
        if hasattr(node.keras_layer, 'batch_dims'):
            batch_dims = node.keras_layer.batch_dims    # type: ignore
        else:
            # default value in tensorflow is 0
            batch_dims = 0

        const_idx = list(quantized_weights.keys())[0]
        assert const_idx == 0, (f"Error in node: {node.name} quantized_weights expect const index 0 got: {const_idx}"
                                f"mctq supports only float32 constants and indices most be int32")

        data = quantized_weights[const_idx].numpy()
        quant = get_quant(node.keras_layer, str(const_idx))
        indices = get_dynamic_inputs(node.keras_layer, inbound_node_index=0)[0]
        TFGatherToNnir.validate(axis, batch_dims, indices, node, len(data.shape))
        request = GraphRequest.request_insert_const_as_input(node.name + f'_const{const_idx}',
                                                             data,
                                                             input_index=const_idx,
                                                             validate_const_insert_at_the_end=False,
                                                             quant=quant)
        return TopKGather(node.name, axis, history=cls.tf_op_history(node)), request
