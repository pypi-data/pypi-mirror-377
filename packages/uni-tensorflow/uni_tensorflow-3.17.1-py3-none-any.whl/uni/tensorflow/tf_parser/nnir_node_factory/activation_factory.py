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
Created on 3/5/23

@author: irenab
"""
from typing import Union, Optional, Type, Callable, Dict, Any    # noqa: F401

from uni.common.core.nnir_graph.nnir_nodes import Softmax, Identity, NnirNode
from uni.common.core.error import supported_vals_msg, raise_op_param_error
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_node_factory import TFNodeFactory, validate_tf
from ._op_activation_mixin import tf_op_activation_to_nnir

tf_softmax_default_axis = -1


def set_activation_factory() -> dict:
    # add activations that are only supported as layer (as opposed to layer param)
    factory: Dict[Any, Optional[Callable]] = {
        'softmax': lambda **kwargs: Softmax(**kwargs, axis=tf_softmax_default_axis)
    }    # yapf: disable
    assert all(k not in tf_op_activation_to_nnir for k in factory.keys())
    factory.update(tf_op_activation_to_nnir)
    return factory


class TFActivationToNnir(TFNodeFactory):
    activation_factory: dict = set_activation_factory()

    supported_activations = list(activation_factory.keys())
    invalid_activation_error = supported_vals_msg(supported_activations)

    @classmethod
    @validate_tf(attrs=['activation'])
    def convert(cls, node: TFMetaNode) -> NnirNode:
        activation = node.get_attr('activation')
        activ_factory = None    # type: Optional[Union[Type[NnirNode], Callable]]
        if activation in cls.activation_factory:
            activ_factory = cls.activation_factory[activation]
            if activ_factory is None:
                activ_factory = Identity
        else:
            raise_op_param_error(cls.tf_op_info(node),
                                 param_name='activation',
                                 param_value=activation,
                                 reason=cls.invalid_activation_error,
                                 history=None)

        assert activ_factory
        return activ_factory(name=node.name)
