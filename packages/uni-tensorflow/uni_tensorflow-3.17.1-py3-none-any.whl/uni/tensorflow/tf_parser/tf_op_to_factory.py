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
Created on 3/27/23

@author: irenab
"""
import tensorflow as tf
from edgemdt_cl.keras import FasterRCNNBoxDecode, SSDPostProcess
from mct_quantizers import KerasQuantizationWrapper
from mct_quantizers.keras.activation_quantization_holder import KerasActivationQuantizationHolder

from uni.tensorflow.keras_import_util import TFOpLambda, SlicingOpLambda
from uni.common.parsers.base_reader import MetaOpType
from .nnir_node_factory import TFAddToNnir, TFConv2dToNnir, TFPlaceholderToNnir, TFMultiplyToNnir, TFReluToNnir, \
    TFIdentityToNnir, TFMetaNodeIdentityToNnir
from .nnir_node_factory import TFReshapeToNnir, TFSoftmaxToNnir, TFSubtractToNnir, TFOpLambdaToNnirDispatcher
from .nnir_node_factory import TFZeroPadding2DToNnir, TFOutputToNnir, TFPermuteToNnir, TFDepthwiseConv2dToNnir
from .nnir_node_factory import TFConcatenateToNnir, TFDenseToNnir, TFLayerNormToNnir, TFGlobalAvgPoolToNnir
from .nnir_node_factory import TFActivationToNnir, TFDummyOutputToNnir, TFFlattenToNnir
from .nnir_node_factory import TFDropoutToNnir, TFMaxPoolToNnir, TFBatchNormToNnir
from .nnir_node_factory import TFAveragePoolToNnir, TFConv2dTransposeToNnir
from .nnir_node_factory import TFLeakyReluToNnir, TFResizingToNnir
from .nnir_node_factory import TFUpSampling2DToNnir
from .nnir_node_factory import TFNativeSliceToNnir
from .nnir_node_factory.binary_op_factory import TFMinToNnir, TFMaxToNnir
from .nnir_node_factory.mct_quantizers_nodes import KerasActivationQuantizationHolderFactory
from .nnir_node_factory.mct_quantizers_nodes import TFKerasQuantizationWrapperFactory
from .nnir_node_factory.custom import TFSSDPostProcessToNnir, TFFasterRCNNBoxDecodeToNnir

kl = tf.keras.layers

tf_op_factory = {
    KerasActivationQuantizationHolder: KerasActivationQuantizationHolderFactory,
    KerasQuantizationWrapper: TFKerasQuantizationWrapperFactory,
    FasterRCNNBoxDecode: TFFasterRCNNBoxDecodeToNnir,
    SSDPostProcess: TFSSDPostProcessToNnir,
    kl.Activation: TFActivationToNnir,
    kl.Add: TFAddToNnir,
    kl.AveragePooling2D: TFAveragePoolToNnir,
    kl.BatchNormalization: TFBatchNormToNnir,
    kl.Concatenate: TFConcatenateToNnir,
    kl.Conv2D: TFConv2dToNnir,
    kl.Conv2DTranspose: TFConv2dTransposeToNnir,
    kl.Dense: TFDenseToNnir,
    kl.DepthwiseConv2D: TFDepthwiseConv2dToNnir,
    kl.Dropout: TFDropoutToNnir,
    kl.Flatten: TFFlattenToNnir,
    kl.GlobalAveragePooling2D: TFGlobalAvgPoolToNnir,
    kl.Identity: TFIdentityToNnir,
    kl.InputLayer: TFPlaceholderToNnir,
    kl.LayerNormalization: TFLayerNormToNnir,
    kl.LeakyReLU: TFLeakyReluToNnir,
    kl.Maximum: TFMaxToNnir,
    kl.MaxPooling2D: TFMaxPoolToNnir,
    kl.Minimum: TFMinToNnir,
    kl.Multiply: TFMultiplyToNnir,
    kl.Permute: TFPermuteToNnir,
    kl.Resizing: TFResizingToNnir,
    kl.ReLU: TFReluToNnir,
    kl.Reshape: TFReshapeToNnir,
    kl.Softmax: TFSoftmaxToNnir,
    kl.Subtract: TFSubtractToNnir,
    kl.UpSampling2D: TFUpSampling2DToNnir,
    kl.ZeroPadding2D: TFZeroPadding2DToNnir,
    SlicingOpLambda: TFNativeSliceToNnir,
    TFOpLambda: TFOpLambdaToNnirDispatcher,
    MetaOpType.NoOp: TFMetaNodeIdentityToNnir,
    MetaOpType.Output: TFOutputToNnir,
    MetaOpType.DummyOutput: TFDummyOutputToNnir,
}
