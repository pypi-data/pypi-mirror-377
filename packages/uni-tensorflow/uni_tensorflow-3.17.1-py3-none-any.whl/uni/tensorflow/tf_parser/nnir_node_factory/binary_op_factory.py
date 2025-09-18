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
Created on 12/18/22

@author: irenab
"""
from abc import ABC

from uni.common.core.error import raise_op_input_error
from .tf_node_factory import TFNodeFactory, validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.common.core.nnir_graph.nnir_nodes import Add, Sub, Mul, Min, Max
from uni.tensorflow.tf_parser import tf_reader_helper


class TFBinKerasOpBase(TFNodeFactory, ABC):
    multi_inputs_err_msg = 'only binary operation is supported'

    @classmethod
    def validate(cls, node: TFMetaNode):
        assert node.inbound_node_index is not None
        input_shape = tf_reader_helper.get_dynamic_input_shapes(node.keras_layer, node.inbound_node_index)
        if len(input_shape) > 2:
            raise_op_input_error(cls.tf_op_info(node),
                                 input_index=2,
                                 input_name='input',
                                 reason=cls.multi_inputs_err_msg,
                                 history=None)


class TFAddToNnir(TFBinKerasOpBase):

    @classmethod
    @validate_tf(attrs=[])
    def convert(cls, node: TFMetaNode) -> Add:
        """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Add """
        cls.validate(node)
        return Add(name=node.name)


class TFSubtractToNnir(TFBinKerasOpBase):

    @classmethod
    @validate_tf(attrs=[])
    def convert(cls, node: TFMetaNode) -> Sub:
        """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Subtract """
        cls.validate(node)
        return Sub(name=node.name)


class TFMultiplyToNnir(TFBinKerasOpBase):

    @classmethod
    @validate_tf(attrs=[])
    def convert(cls, node: TFMetaNode) -> Mul:
        """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Multiply """
        cls.validate(node)
        return Mul(name=node.name)


class TFMinToNnir(TFNodeFactory):

    @classmethod
    @validate_tf(attrs=[])
    def convert(cls, node: TFMetaNode) -> Min:
        """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Minimum """
        return Min(name=node.name)


class TFMaxToNnir(TFNodeFactory):

    @classmethod
    @validate_tf(attrs=[])
    def convert(cls, node: TFMetaNode) -> Max:
        """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Maximum """
        return Max(name=node.name)
