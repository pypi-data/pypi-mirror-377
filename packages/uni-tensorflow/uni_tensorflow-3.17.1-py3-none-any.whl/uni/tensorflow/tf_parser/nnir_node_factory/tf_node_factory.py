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
import abc
from typing import Union, Tuple, Optional, List
import functools

from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.node_history import NodeHistory
from uni.common.core.common import OpInfo, Framework
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.tensorflow.tf_parser import tf_reader_helper

common_attrs = ['name', 'trainable', 'dtype', 'training']


def validate_tf(attrs: Optional[List[str]] = None,
                optional_attrs: Optional[List[str]] = None,
                call_kwargs: Optional[List[str]] = None,
                optional_call_kwargs: Optional[List[str]] = None,
                skip_call_kwargs=False,
                skip=False):
    """ TF Op validation decorator for TF factory
        attrs: a list of expected mandatory attributes. Empty list if none are expected.
               Must be None if skip=True.
        call_kwargs: a list of expected mandatory call_kwargs. Empty list if none are expected.
        optional_call_kwargs: a list of allowed optional call kwargs. None or [] if none are expected.
                              Must be None if skip_call_kwargs=True.
        skip_call_kwargs: skip call kwargs validation. optional_call_kwarg must be None
        skip: skip the whole validation (overrides skip_call_kwargs=False). attrs and optional_call_kwargs must be None
    """
    if attrs is None and skip is False:
        raise ValueError('attrs can be None only with skip_attr=True. If node has no attributes, pass []')
    if skip and (attrs is not None or optional_call_kwargs is not None):
        raise ValueError('ambiguous params: both non-None attrs/optional_call_kwargs and skip were passed')
    if skip_call_kwargs and optional_call_kwargs is not None:
        raise ValueError('ambiguous params: both skip_call_kwargs and optional_call_kwargs were passed')
    if optional_attrs is None:
        optional_attrs = []
    if call_kwargs is None:
        call_kwargs = []
    if optional_call_kwargs is None:
        optional_call_kwargs = []

    def decorator(func):

        @functools.wraps(func)
        def decorated(cls, tf_node: TFMetaNode):
            if not skip:
                assert attrs is not None    # for mypy
                actual_attrs = tf_reader_helper.get_keras_op_attrs(tf_node.keras_layer).keys()
                missing_attrs = [a for a in attrs if a not in actual_attrs]
                unknown_attrs = [a for a in actual_attrs if a not in attrs + common_attrs + optional_attrs]

                missing_kwargs = []
                unknown_kwargs = []
                if not skip_call_kwargs:
                    actual_call_kwargs = tf_reader_helper.get_call_kwargs(tf_node.keras_layer)
                    assert optional_call_kwargs is not None    # for mypy
                    missing_kwargs = [a for a in call_kwargs if a not in actual_call_kwargs]
                    unknown_kwargs = [
                        a for a in actual_call_kwargs if a not in optional_call_kwargs + call_kwargs + common_attrs
                    ]

                if missing_attrs or unknown_attrs or missing_kwargs or unknown_kwargs:
                    raise ValueError(f'Missing or unknown attrs for op {tf_node.op}: '
                                     f'attrs: missing {missing_attrs}, unknown {unknown_attrs}, '
                                     f'call_kwargs: missing {missing_kwargs}, unknown {unknown_kwargs}')
            return func(cls, tf_node)

        # mark function as decorated so that it can be validated
        decorated.valid = True    # type: ignore[attr-defined]
        return decorated

    return decorator


class TFNodeFactory(abc.ABC):
    # inject reader helper for usage convenience
    tf_reader_helper = tf_reader_helper

    @classmethod
    @abc.abstractmethod
    def convert(cls, node: TFMetaNode) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        pass

    @staticmethod
    def tf_op_info(node: TFMetaNode):
        return OpInfo(node_id=node.name, op=node.tf_op_full_name(), framework=Framework.tensorflow)

    @classmethod
    def get_history(cls, node: TFMetaNode, desc: Optional[str] = None) -> NodeHistory:
        return NodeHistory(op_info=cls.tf_op_info(node), desc=desc)

    @classmethod
    def is_supported_node(cls, node: TFMetaNode) -> bool:
        """ to be overridden by factories that handle more than one op (e.g. TfOpLambda)
            so that supported ops can be validated before conversion """
        return True
