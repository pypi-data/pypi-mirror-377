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
from .mct_quantizers_nodes import TFMctFactoryBase

from .activation_factory import TFActivationToNnir
from .batch_norm_factory import TFBatchNormToNnir
from .binary_op_factory import TFAddToNnir, TFSubtractToNnir, TFMultiplyToNnir
from .concat_factory import TFConcatenateToNnir
from .conv2d_factory import TFConv2dToNnir
from .conv2dtranspose_factory import TFConv2dTransposeToNnir
from .dense_factory import TFDenseToNnir
from .depthwise_conv2d_factory import TFDepthwiseConv2dToNnir
from .dropout_factory import TFDropoutToNnir
from .dummy_output_factory import TFDummyOutputToNnir
from .flatten_factory import TFFlattenToNnir
from .global_pool_factories import TFGlobalAvgPoolToNnir
from .identity_factory import TFIdentityToNnir, TFMetaNodeIdentityToNnir
from .layer_norm_factory import TFLayerNormToNnir
from .leaky_relu_factory import TFLeakyReluToNnir
from .native_slice_factory import TFNativeSliceToNnir
from .output_factory import TFOutputToNnir
from .permute_factory import TFPermuteToNnir
from .placeholder_factory import TFPlaceholderToNnir
from .pool_factories import TFAveragePoolToNnir, TFMaxPoolToNnir
from .relu_factory import TFReluToNnir
from .reshape_factory import TFReshapeToNnir
from .resizing_factory import TFResizingToNnir
from .softmax_factory import TFSoftmaxToNnir
from .tf_op_lambda_factory import TFOpLambdaToNnirDispatcher
from .upsample2d_factory import TFUpSampling2DToNnir
from .zero_padding2d_factory import TFZeroPadding2DToNnir
