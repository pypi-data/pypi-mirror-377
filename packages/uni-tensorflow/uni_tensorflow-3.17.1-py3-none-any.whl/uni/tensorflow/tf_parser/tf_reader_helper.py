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
import copy
from typing import List, Tuple, Callable, Optional, Union, Any, Dict

import numpy as np
import tensorflow as tf
from uni.tensorflow.keras_import_util import KerasTensor, TFOpLambda


def get_inbound_nodes(keras_layer: tf.keras.layers.Layer):
    return keras_layer.inbound_nodes


def get_dynamic_inputs(keras_layer: tf.keras.layers.Layer, inbound_node_index: int) -> List[KerasTensor]:
    # layer.input cannot be used since sometimes it doesn't contain all inputs (e.g. for tf.math.truediv it only
    # contains one input, even when it has 2 dynamic inputs)
    # so keras_inputs of inbound_nodes should be used for connectivity
    inbound_node = get_inbound_nodes(keras_layer)[inbound_node_index]
    return _as_list(inbound_node.keras_inputs)


def get_dynamic_input_shapes(keras_layer: tf.keras.layers.Layer, inbound_node_index: int) -> List[tuple]:
    return [tuple(t.shape) for t in get_dynamic_inputs(keras_layer, inbound_node_index)]


def get_layer_output_shapes(keras_layer: tf.keras.layers.Layer, inbound_node_index) -> List[tuple]:
    node = get_inbound_nodes(keras_layer)[inbound_node_index]
    output_shapes = node.output_shapes
    if output_shapes is not None:    # None can be in squeeze empty axis
        if isinstance(output_shapes, dict):
            orders_keys = sorted(output_shapes.keys(), key=lambda k: get_tensor_index(node.outputs[k]))
            return [output_shapes[k] for k in orders_keys]
        #  checking if list of shapes/tuple or only one shape
        if len(output_shapes) > 0 and isinstance(output_shapes[0], Tuple):    # type: ignore [arg-type]
            return output_shapes
    return [output_shapes]


def get_inbound_layers(keras_layer: tf.keras.layers.Layer,
                       inbound_node_index) -> Union[List[tf.keras.layers.Layer], tf.keras.layers.Layer]:
    return get_inbound_nodes(keras_layer)[inbound_node_index].inbound_layers


def get_keras_op_attrs(keras_layer: tf.keras.layers.Layer) -> dict:
    # for keras layers this contains all op's attributes """
    return keras_layer.get_config()


def get_tf_op_lambda_op(keras_layer: tf.keras.layers.Layer) -> str:
    assert isinstance(keras_layer, TFOpLambda)
    return keras_layer.get_config()['function']


def get_tf_op_lambda_attrs(keras_layer: tf.keras.layers.Layer) -> Tuple[tuple, dict, Callable]:
    """ Returns:
        - OpLambda attributes as a dict
        - Callable for retrieving default values (either by key or as dict).
          Default values are obtained from tf op signature. The code is very brittle,
          so we provide a callable instead of populating attrs with default values in advance.
          (Keras stores tf attributes under call_kwargs, so we assume there is a direct mapping between the two)
          """
    assert isinstance(keras_layer, TFOpLambda)
    call_kwargs = get_call_kwargs(keras_layer)
    call_args = get_call_args(keras_layer)

    def defaults_getter(attr: Optional[str] = None) -> Union[Any, Dict[str, Any]]:
        import inspect
        params = inspect.signature(keras_layer.call).parameters
        default_params = {p: v.default for p, v in params.items() if v.default is not v.empty}
        if attr is None:
            return default_params
        if attr not in default_params:
            op = get_tf_op_lambda_op(keras_layer)
            raise ValueError(f'Failed to obtain the default value for attribute {attr} of op {op}')
        return default_params[attr]

    return call_args, call_kwargs, defaults_getter


def get_call_kwargs(keras_layer: tf.keras.layers.Layer) -> dict:
    inbound_node = get_inbound_nodes(keras_layer)[0]
    return inbound_node.call_kwargs


def get_call_args(keras_layer: tf.keras.layers.Layer) -> tuple:
    inbound_node = get_inbound_nodes(keras_layer)[0]
    return inbound_node.call_args


def get_kernel(keras_layer: tf.keras.layers.Layer, kernel_attr) -> np.ndarray:
    if hasattr(keras_layer, kernel_attr):
        return getattr(keras_layer, kernel_attr).numpy()
    raise ValueError(f'Failed to obtain the {kernel_attr} of layer {keras_layer.name}')


def get_bias(keras_layer: tf.keras.layers.Layer) -> Optional[np.ndarray]:
    if keras_layer.bias is None:
        return None
    return keras_layer.bias.numpy()


def get_weights(keras_layer: tf.keras.layers.Layer) -> List[np.ndarray]:
    return keras_layer.get_weights()


def _as_list(obj):
    return list(obj) if isinstance(obj, (list, tuple)) else [obj]


def is_tensor(obj):
    return isinstance(obj, KerasTensor)


def get_rank(tensor: KerasTensor) -> int:
    return tensor.shape.rank


def get_shape(tensor: KerasTensor) -> tuple:
    res = list(tensor.shape)
    if res[0] is None:
        res[0] = 1
    # after last if statement, no None should be in res
    if None in res:
        raise ValueError(f"None value is only supported for batch axis, got: {tensor.shape}\n")
    return tuple(res)


def get_input(layer: tf.keras.layers.Layer):
    return layer.input


def get_tensor_index(tensor: KerasTensor):
    # noinspection PyProtectedMember
    return tensor._keras_history.tensor_index


def clone_layer(layer, new_name):
    # using deep copy can fail
    old_name = layer.name
    new_layer = copy.copy(layer)
    new_layer._name = new_name
    assert new_layer.name == new_name
    assert layer.name == old_name
    return new_layer


def layer_is_model(layer) -> bool:
    return isinstance(layer, tf.keras.Model)
