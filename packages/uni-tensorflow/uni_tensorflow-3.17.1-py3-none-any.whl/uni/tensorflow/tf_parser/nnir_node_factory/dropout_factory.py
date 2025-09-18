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
Created on 2/9/23

@author: irenab
"""
from uni.common.core.nnir_graph.nnir_nodes import Identity
from uni.common.core.error import raise_op_param_error, training_mode_error
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_node_factory import TFNodeFactory, validate_tf


class TFDropoutToNnir(TFNodeFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/keras/layers/Dropout """

    @classmethod
    @validate_tf(attrs=['rate', 'noise_shape', 'seed'], optional_call_kwargs=['training'])
    def convert(cls, node: TFMetaNode) -> Identity:
        # Real networks will probably always contain the default training=None which means use the training phase,
        # but we accept explicit training=False as well
        train = cls.tf_reader_helper.get_call_kwargs(node.keras_layer).get('training')
        if train:
            raise_op_param_error(cls.tf_op_info(node), 'Call arg: training', train, training_mode_error, None)

        return Identity(node.name, history=cls.get_history(node, 'Dropout -> Identity'))
