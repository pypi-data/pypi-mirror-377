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
from mct_quantizers.keras.quantizers import ActivationPOTInferableQuantizer

from uni.common.core.error import supported_vals_msg
from uni.common.core.nnir_graph.nnir_nodes import Quant
from uni.common.core.nnir_graph.quant_info import SymmetricQuantInfo
from uni.tensorflow.tf_parser.nnir_node_factory.mct_quantizers_nodes import TFMctFactoryBase
from uni.tensorflow.tf_parser.nnir_node_factory.tf_node_factory import validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode


class KerasActivationQuantizationHolderFactory(TFMctFactoryBase):

    supported_params = ["activation_holder_quantizer"]
    supported_msg = supported_vals_msg(supported_params)

    @classmethod
    def is_supported_node(cls, node: TFMetaNode) -> bool:
        quantizer = node.keras_layer.activation_holder_quantizer    # type: ignore
        return isinstance(quantizer, ActivationPOTInferableQuantizer)

    @classmethod
    @validate_tf(attrs=['activation_holder_quantizer', 'mctq_version'])
    def convert(cls, node: TFMetaNode) -> Quant:
        quantizer = node.keras_layer.activation_holder_quantizer    # type: ignore
        assert isinstance(quantizer, ActivationPOTInferableQuantizer)
        assert len(quantizer.threshold) == 1
        threshold = quantizer.threshold[0]
        num_bits = quantizer.num_bits
        quant_info = SymmetricQuantInfo(value_n_bits=num_bits, threshold=threshold, signed=quantizer.signed)
        return Quant(name=node.name, quant_info=quant_info)

    @classmethod
    def get_op_inner_name(cls, node: TFMetaNode):
        return node.keras_layer.activation_holder_quantizer.__class__.__name__    # type: ignore
