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
Created on 1/16/23

@author: irenab
"""
from uni.common.core.nnir_graph.nnir_nodes import Swish
from uni.common.core.node_history import NodeHistory
from uni.common.core.error import supported_vals_msg, raise_op_param_error
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from .tf_op_lambda_factory_base import TFOpLambdaToNnirFactory, validate_tf_op_lambda, OpLambdaAttrs


class TFSiluToNnir(TFOpLambdaToNnirFactory):
    """ https://www.tensorflow.org/api_docs/python/tf/nn/silu
        https://www.tensorflow.org/api_docs/python/tf/nn/swish (alias) """
    supported_beta = [1.]
    unsupported_beta_error = supported_vals_msg(supported_beta)

    @classmethod
    @validate_tf_op_lambda(attrs=[], optional_attrs=['beta'])
    def convert(cls, node: TFMetaNode, attrs: OpLambdaAttrs) -> Swish:
        beta = attrs.get('beta')
        if beta != 1.:
            raise_op_param_error(cls.tf_op_info(node), 'beta', beta, reason=cls.unsupported_beta_error, history=None)
        return Swish(node.name, NodeHistory(cls.tf_op_info(node)))
