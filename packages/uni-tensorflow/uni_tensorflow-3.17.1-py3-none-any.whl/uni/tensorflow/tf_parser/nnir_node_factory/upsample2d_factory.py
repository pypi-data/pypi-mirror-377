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
Created on 8/27/23

@author: irenab
"""
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode

from uni.common.core.nnir_graph.nnir_nodes import Resize
from .resize_factory_base import TFResizeToNnirBase


class TFUpSampling2DToNnir(TFResizeToNnirBase):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/UpSampling2D """

    fw_method_attr_name = 'interpolation'

    @classmethod
    @validate_tf(attrs=['size', 'data_format', fw_method_attr_name])
    def convert(cls, tf_node: TFMetaNode) -> Resize:
        cls.validate_data_format(tf_node)

        factor_h, factor_w = tf_node.get_attr('size')
        method = tf_node.get_attr(cls.fw_method_attr_name)
        assert tf_node.inbound_node_index is not None
        input_shape = cls.tf_reader_helper.get_dynamic_input_shapes(tf_node.keras_layer, tf_node.inbound_node_index)[0]
        h, w = cls.get_hw(input_shape)
        target_size = factor_h * h, factor_w * w
        return cls.base_convert(tf_node, target_size, method, errors=[])
