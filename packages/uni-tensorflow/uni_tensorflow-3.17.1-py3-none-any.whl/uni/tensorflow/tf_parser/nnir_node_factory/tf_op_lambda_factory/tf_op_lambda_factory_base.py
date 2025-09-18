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
import abc
from typing import Union, Tuple, Callable, List, Optional
import functools
from dataclasses import dataclass

from uni.common.core.common import OpInfo, Framework
from uni.common.util.dev import is_dev
from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.node_history import NodeHistory
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser.tf_reader_helper import get_tf_op_lambda_op, get_dynamic_inputs, get_dynamic_input_shapes


@dataclass
class OpLambdaAttrs:
    """
    OpLambda attributes helper
    attrs['foo'] - retrieve a mandatory attribute
    attrs.get('bar') - retrieve an optiona attribute. If not present, default tf value will be fetched
    """
    call_args: Tuple
    explicit_attrs: dict
    defaults_getter: Callable

    def __getitem__(self, key):
        return self.explicit_attrs[key]

    def get(self, key):
        if key in self.explicit_attrs:
            return self.explicit_attrs[key]
        return self.defaults_getter(key)


def validate_tf_op_lambda(attrs: List[str], optional_attrs: Optional[List[str]] = None):
    """ Attributes validator decorator for convert method of OpLambdaFactory
        Arguments:
            attrs: mandatory expected attributes
            optional_attrs: if not passed explicitly, it's expected to be retrievable from tf defaults
                            (for now this part is only validated if DEV env is set. In production, we fetch defaults
                             only if needed, since this code is a bit risky')
    """
    if optional_attrs is None:
        optional_attrs = []
    known_attrs = attrs + optional_attrs + ['name', 'training']

    def decorator(func):

        @functools.wraps(func)
        def decorated(cls, node, op_attrs: OpLambdaAttrs):
            missing_attrs = [a for a in attrs if a not in op_attrs.explicit_attrs]
            unknown_attrs = [a for a in op_attrs.explicit_attrs if a not in known_attrs]

            missing_defaults = []
            unknown_defaults = []
            if is_dev():
                default_params: dict = op_attrs.defaults_getter()
                assert isinstance(optional_attrs, list)    # for mypy
                missing_defaults = [p for p in optional_attrs if p not in default_params]
                unknown_defaults = [p for p in default_params if p not in known_attrs]

            if missing_attrs or unknown_attrs or missing_defaults or unknown_defaults:
                raise ValueError(f'Missing or unknown attrs for op {get_tf_op_lambda_op(node.keras_layer)}. '
                                 f'Mandatory: missing {missing_attrs}, unknown {unknown_attrs}, '
                                 f'Optional: missing {missing_defaults}, unknown {unknown_defaults}')

            return func(cls, node, op_attrs)

        # mark function as decorated so that it can be validated
        decorated.valid = True    # type: ignore[attr-defined]
        return decorated

    return decorator


class TFOpLambdaToNnirFactory(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def convert(node: TFMetaNode, attrs: OpLambdaAttrs) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        pass

    @staticmethod
    def tf_op_info(node: TFMetaNode):
        op = node.keras_layer.__class__.__name__ + '::' + get_tf_op_lambda_op(node.keras_layer)
        return OpInfo(node_id=node.name, op=op, framework=Framework.tensorflow)

    @classmethod
    def tf_op_history(cls, node, desc=None):
        return NodeHistory(cls.tf_op_info(node), desc=desc)

    @classmethod
    def get_dynamic_inputs(cls, node: TFMetaNode):
        assert node.inbound_node_index is not None
        return get_dynamic_inputs(node.keras_layer, inbound_node_index=node.inbound_node_index)

    @classmethod
    def get_dynamic_input_shapes(cls, node):
        assert node.inbound_node_index is not None
        return get_dynamic_input_shapes(node.keras_layer, node.inbound_node_index)
