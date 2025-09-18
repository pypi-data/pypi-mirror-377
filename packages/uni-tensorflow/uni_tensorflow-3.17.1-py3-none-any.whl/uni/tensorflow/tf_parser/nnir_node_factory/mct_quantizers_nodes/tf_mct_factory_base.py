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
from abc import ABC, abstractmethod

from uni.common.core.common import OpInfo, Framework
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import TFNodeFactory
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode


class TFMctFactoryBase(TFNodeFactory, ABC):

    @classmethod
    def tf_op_info(cls, node: TFMetaNode):
        op = node.keras_layer.__class__.__name__ + '::' + cls.get_op_inner_name(node)
        return OpInfo(node_id=node.name, op=op, framework=Framework.tensorflow)

    @classmethod
    @abstractmethod
    def get_op_inner_name(cls, node: TFMetaNode):
        raise NotImplementedError
