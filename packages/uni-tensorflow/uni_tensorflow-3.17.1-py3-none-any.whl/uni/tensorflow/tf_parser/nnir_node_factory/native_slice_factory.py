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
from typing import Tuple, Optional

from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeToInsertCfg, NodePosition
from uni.common.core.nnir_graph.nnir_nodes import StridedSlice, Squeeze
from .tf_node_factory import TFNodeFactory, validate_tf
from uni.tensorflow.tf_parser.tf_meta_node import TFMetaNode
from uni.common.core.error import ParamErrorInfo, raise_op_error


class TFNativeSliceToNnir(TFNodeFactory):

    _unsupported_ops = {type(None): 'new axis is not supported', type(Ellipsis): 'Ellipsis is not supported'}
    select_along_batch_axis_error = 'Index selection along the batch axis is not supported'

    @classmethod
    @validate_tf(attrs=['function'], call_kwargs=['slice_spec'])
    def convert(cls, node: TFMetaNode) -> Tuple[StridedSlice, Optional[GraphRequest]]:
        spec = cls.tf_reader_helper.get_call_kwargs(node.keras_layer)['slice_spec']

        errors = []
        for axis, axis_spec in enumerate(spec):
            msg = cls._unsupported_ops.get(type(axis_spec))
            if msg:
                errors.append(ParamErrorInfo(f'slice_spec for axis {axis}', axis_spec, msg))
            elif axis == 0 and isinstance(axis_spec, int):
                errors.append(
                    ParamErrorInfo(f'slice_spec for axis {axis}', axis_spec, cls.select_along_batch_axis_error))

        if errors:
            raise_op_error(cls.tf_op_info(node), errors, history=None)

        begin = []
        end = []
        strides = []
        squeeze_dims = []
        for i, axis_spec in enumerate(spec):
            if isinstance(axis_spec, dict):
                begin.append(axis_spec['start'])
                end.append(axis_spec['stop'])
                strides.append(axis_spec['step'])
            elif isinstance(axis_spec, int):
                begin.append(axis_spec)
                end.append(None if axis_spec == -1 else axis_spec + 1)
                strides.append(1)
                squeeze_dims.append(i)
            else:
                raise TypeError(f'Unexpected spec type {type(axis_spec)}')

        begin, begin_mask = cls.extract_mask(begin)
        end, end_mask = cls.extract_mask(end)
        # replace None
        strides = [1 if s is None else s for s in strides]

        request = None
        if squeeze_dims:
            squeeze = Squeeze(node.name + '_squeeze', squeeze_dims=squeeze_dims)
            input_shape = cls.tf_reader_helper.get_dynamic_input_shapes(node.keras_layer, node.inbound_node_index)[0]
            request = GraphRequest(
                adjacent_node_to_insert=NodeToInsertCfg(squeeze, input_shape, NodePosition.NODE_AFTER))

        desc = f'{node.keras_layer.__class__.__name__} -> {StridedSlice.op}'
        if squeeze_dims:
            desc += f' + {Squeeze.op}'
        history = cls.get_history(node, desc=desc)
        strided_slice = StridedSlice(node.name,
                                     begin=begin,
                                     end=end,
                                     strides=strides,
                                     begin_mask=begin_mask,
                                     end_mask=end_mask,
                                     history=history)

        return strided_slice, request

    @staticmethod
    def extract_mask(vals):
        masked_axes = [i for i, v in enumerate(vals) if v is None]
        mask = StridedSlice.calculate_mask(masked_axes)
        # replace masked values with any valid index
        final_vals = [v if v else 0 for v in vals]
        return final_vals, mask
