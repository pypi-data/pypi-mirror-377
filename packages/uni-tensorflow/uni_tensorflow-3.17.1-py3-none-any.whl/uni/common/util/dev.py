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
Created on 2/2/23

@author: irenab
"""
import os

DEV_ENV = 'UNI_DEV'
SKIP_COMPLIANCE_CHECK = 'UNI_SKIP_COMPLIANCE_CHECK'
DISABLE_SIMPLIFIER = 'UNI_DISABLE_SIMPLIFIER'
SKIP_VALIDATE_INPUT = 'SKIP_VALIDATE_INPUT'
STRICT_VALIDATION = 'STRICT_VALIDATION'
SAVE_SIMPLIFIER = 'SAVE_SIMPLIFIER'


def is_dev():
    dev = os.getenv(DEV_ENV)
    return dev and int(dev)


def skip_compliance_check():
    """ Whether to skip nodes compliance validation """
    disable = os.getenv(SKIP_COMPLIANCE_CHECK)
    return disable and int(disable)


def disable_simplifier():
    disable = os.getenv(DISABLE_SIMPLIFIER)
    return disable and int(disable)


def is_skip_validate_input():
    return os.getenv(SKIP_VALIDATE_INPUT) == "1"


def set_validate_input(validate_input: bool):
    os.environ['SKIP_VALIDATE_INPUT'] = "0" if validate_input else "1"


def is_strict_validation():
    return os.getenv(STRICT_VALIDATION) == "1"


def set_strict_validation(strict_validation: bool):
    os.environ['STRICT_VALIDATION'] = "1" if strict_validation else "0"


def is_save_simplifier():
    return os.getenv(SAVE_SIMPLIFIER) == "1"


def set_save_simplifier(save_simplifier: bool):
    os.environ['SAVE_SIMPLIFIER'] = "1" if save_simplifier else "0"
