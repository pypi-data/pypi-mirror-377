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
import tensorflow as tf
from dataclasses import dataclass, field, replace
from typing import Optional, Union, cast

from uni.common.parsers.base_reader import MetaOpType
from .tf_reader_helper import get_keras_op_attrs


@dataclass
class TFMetaNode:
    name: str
    op: Union[type, MetaOpType]    # MetaOpType for "fake" TFMetaNode
    keras_layer: Optional[tf.keras.layers.Layer]    # original keras_layer, allowing None only for "fake" TFMetaNode
    inbound_node_index: Optional[int]
    shared_group_id: Optional[str] = None    # in layer sharing when coping node this point to original node
    extra: Optional[dict] = None
    attr: dict = field(init=False, default_factory=dict)
    inner_op_name: str = field(init=False)

    def __post_init__(self):
        self.inner_op_name = ""
        assert self.keras_layer or isinstance(self.op, MetaOpType)
        if self.keras_layer:
            self.keras_attr = get_keras_op_attrs(self.keras_layer)
            if isinstance(self.keras_layer, tf.keras.layers.Wrapper):
                self.inner_op_name = self.keras_layer.layer.name

    def clone(self, **kwargs):
        return replace(self, **kwargs)

    @property
    def key(self):
        return self.name

    def get_attr(self, attr):
        return self.keras_attr[attr]

    def __getitem__(self, attr):
        return self.keras_attr[attr]

    def tf_op_full_name(self) -> str:
        """ op full name, e.g. keras.layers.activations.relu.ReLU """
        assert isinstance(self.op, MetaOpType) is False
        op = cast(type, self.op)    # for mypy
        res = op.__module__ + '.' + op.__name__
        if self.inner_op_name:
            res += ':' + self.inner_op_name
        return res

    def tf_op_short_name(self) -> str:
        assert isinstance(self.op, MetaOpType) is False
        res = cast(type, self.op).__name__    # for mypy
        if self.inner_op_name:
            res += ':' + self.inner_op_name
        return res
