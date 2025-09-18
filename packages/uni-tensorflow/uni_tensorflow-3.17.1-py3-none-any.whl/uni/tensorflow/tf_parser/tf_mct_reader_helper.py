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
from typing import Optional

import tensorflow as tf

from mct_quantizers.keras.quantizers import WeightsPOTInferableQuantizer, WeightsSymmetricInferableQuantizer, \
     WeightsLUTPOTInferableQuantizer, WeightsLUTSymmetricInferableQuantizer
from uni.common.core.nnir_graph.quant_info import LUTPerChannelQuantInfo, LUTQuantInfo, QuantInfoBase, \
    SymmetricQuantInfo, SymmetricPerChannelQuantInfo

MCT_WEIGHTS_SYMMETRIC_QUANT_CLASS = [WeightsPOTInferableQuantizer, WeightsSymmetricInferableQuantizer]
MCT_WEIGHTS_LUT_QUANT_CLASS = [WeightsLUTPOTInferableQuantizer, WeightsLUTSymmetricInferableQuantizer]


def get_quant(keras_layer: tf.keras.layers.Layer, attr_name: str) -> Optional[QuantInfoBase]:
    quant: Optional[WeightsSymmetricInferableQuantizer] = None
    if hasattr(keras_layer, 'get_weights_vars'):
        for name, tensor, _quant, in keras_layer.get_weights_vars():
            # convert to str for in like (0, 1, 2) for MCTQ const bin quant
            if str(name) == attr_name:
                quant = _quant
                break
    if quant is None:
        return None

    if any(issubclass(quant.__class__, _class) for _class in MCT_WEIGHTS_SYMMETRIC_QUANT_CLASS):
        return convert_symmetric_weights_quantizer(quant)

    if any(issubclass(quant.__class__, _class) for _class in MCT_WEIGHTS_LUT_QUANT_CLASS):
        return convert_lut_weights_quantizer(quant)

    raise ValueError(f"Unknown quant {type(quant)} for {attr_name} in node {keras_layer.name}")


def convert_symmetric_weights_quantizer(quant: WeightsSymmetricInferableQuantizer) -> QuantInfoBase:
    assert any(issubclass(quant.__class__, _class) for _class in MCT_WEIGHTS_SYMMETRIC_QUANT_CLASS)
    if not quant.per_channel:
        assert len(quant.threshold) == 1
        return SymmetricQuantInfo(threshold=quant.threshold[0], signed=quant.signed, value_n_bits=quant.num_bits)
    else:
        return SymmetricPerChannelQuantInfo(thresholds=tuple(quant.threshold),
                                            signed=quant.signed,
                                            value_n_bits=quant.num_bits,
                                            axis=quant.channel_axis)


def convert_lut_weights_quantizer(quant: WeightsLUTSymmetricInferableQuantizer) -> QuantInfoBase:
    assert any(issubclass(quant.__class__, _class) for _class in MCT_WEIGHTS_LUT_QUANT_CLASS)
    lut_values = tuple(quant.lut_values)
    if not quant.per_channel:
        assert len(quant.threshold) == 1
        return LUTQuantInfo(lut_values=lut_values,
                            value_n_bits=quant.num_bits,
                            lut_values_bitwidth=quant.lut_values_bitwidth,
                            threshold=quant.threshold[0],
                            signed=quant.signed)
    else:
        return LUTPerChannelQuantInfo(lut_values=lut_values,
                                      value_n_bits=quant.num_bits,
                                      axis=quant.channel_axis,
                                      lut_values_bitwidth=quant.lut_values_bitwidth,
                                      thresholds=tuple(quant.threshold),
                                      signed=quant.signed)
