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
Created on 10/13/22

@author: irenab
"""
from typing import Sequence, Optional, List

from .defs import OpInfo, OpInputErrorInfo, ParamErrorInfo, OpErrorsInfo, InvalidOpError, ErrorInfo, \
                   OpOutputErrorInfo, OpIncorrectNumberOfInputsErrorInfo
from uni.common.core.node_history import NodeHistory

training_mode_error = 'Received op in training mode'


def supported_vals_msg(vals: Sequence):
    return f'Supported values: {list(vals)}'


def exceeds_limit_msg(desc, limit):
    return f'{desc} exceeds the supported limit of {limit}'


def raise_op_param_error(op_info: OpInfo, param_name, param_value, reason, history: Optional[NodeHistory]):
    """ Utility wrapper to raise InvalidOpError with a single param error """
    err = ParamErrorInfo(name=param_name, value=param_value, reason=reason)
    raise_op_error(op_info, [err], history)


def raise_op_input_error(op_info: OpInfo, input_index, input_name, reason, history: Optional[NodeHistory]):
    """ Utility wrapper to raise InvalidOpError with a single input error """
    err = OpInputErrorInfo(input_index=input_index, input_name=input_name, reason=reason)
    raise_op_error(op_info, [err], history)


def raise_op_output_error(op_info: OpInfo, output_index, output_name, reason, history: Optional[NodeHistory]):
    """ Utility wrapper to raise InvalidOpError with a single output error """
    err = OpOutputErrorInfo(output_index=output_index, output_name=output_name, reason=reason)
    raise_op_error(op_info, [err], history)


def raise_op_error(op_info: OpInfo, errors: Sequence[ErrorInfo], history: Optional[NodeHistory]):
    """ Utility wrapper to raise InvalidOpError from a list of op errors """
    assert len(errors)
    orig_op = history.op_info if history else None
    op_err = OpErrorsInfo(op_info, errors=errors, orig_op_info=orig_op)
    raise InvalidOpError(op_errors=op_err)


def raise_incorrect_number_of_inputs(op_info: OpInfo, expected_num_inputs: List[int], actual_num_inputs: int, reason,
                                     history: Optional[NodeHistory]):
    err = OpIncorrectNumberOfInputsErrorInfo(expected_num_inputs, actual_num_inputs, reason=reason)
    raise_op_error(op_info, [err], history)
