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
from uni.common.core.nnir_graph.nnir_nodes import Split
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFSplitToNnir(TFOpLambdaToNnirFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/split """

    @classmethod
    @validate_tf_op_lambda(attrs=['num_or_size_splits'], optional_attrs=['axis', 'num'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Split:
        # Per documentation: "num" is used to specify the number of outputs when it
        # cannot be inferred from the shape of `size_splits`
        # It's not clear when (and if at all) this can happen. Furthermore, if both integer num_or_size_splits
        # and num are passed, and they don't match, tf (2.11) uses num_or_size_splits without error
        # So for now, we expect to get num_or_size_splits and ignore "num"
        num_splits_or_sizes = attrs['num_or_size_splits']
        axis = attrs.get('axis')
        return Split(node.name, axis=axis, num_splits_or_sizes=num_splits_or_sizes)
