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
Created on 8/10/22

@author: irenab
"""
from enum import Enum, auto
import copy
from typing import Optional, Tuple
"""
Semantics - node's semantics for inputs or outputs (separate Semantics object for inputs and for outputs).
Contains TensorSemantics per each input/output in input/output Semantics.
Semantics length should always match the number of inputs/outputs (as they are known).
If tensor semantics is unknown, including its shape, it's set to None.
If a node has a single input/output, Semantics object must still be created with a single TensorSemantics!!!

TensorSemantics - semantics for a single tensor (=single input/output), contains AxisSemantics for each axis.
If tensor shape is known, TensorSemantics must be set, its length should match the shape,
and each axis must have AxisSemantics - may be AxisSemantics.UNKNOWN
If shape is not known, TensorSemantics must not be created.
Example:
for 2d input: TensorSemantics(AxisSemantics.UNKNOWN, AxisSemantics.UNKNOWN) - OK
              TensorSemantics() - WRONG (expected 2 values for 2d tensor)
              TensorSemantics(AxisSemantics.HEIGHT, AxisSemantics.UNKNOWN) - OK
              TensorSemantics(AxisSemantics.HEIGHT, None) - WRONG (None is illegal)
              TensorSemantics(AxisSemantics.BATCH) - WRONG (expected 2 values for 2d tensor)

AxisSemantics - semantics for a specific axis of a tensor
If unknown, must be set to AxisSemantics.UNKNOWN


Examples (assuming input semantics):

Semantics() -> node has no inputs.
Semantics(None) - node has exactly one input, but its shape is unknown.
Semantics(TensorSemantics(AxisSemantic.BATCH, AxisSemantics.UNKNOWN), None) - node has exactly two inputs,
first one has exactly 2 axes, second one is unknown.
"""


class DataFormat(Enum):
    CHW = auto()
    HWC = auto()

    def get_hw_axes(self) -> Tuple[int, int]:
        helper = SemanticsHelper(self)
        return helper.data_h_axis(), helper.data_w_axis()

    def get_c_axis(self):
        helper = SemanticsHelper(self)
        return helper.axis_by_semantics(AxisSemantics.CHANNELS)


class AxisSemantics(Enum):
    """ Semantics for a single axis
        Enum names currently match string values in layer_model
    """
    BATCH = auto()
    HEIGHT = auto()
    WIDTH = auto()
    CHANNELS = auto()
    IN_CHANNELS = auto()    # in weights
    OUT_CHANNELS = auto()    # in weight
    KERNEL_H = auto()
    KERNEL_W = auto()
    UNKNOWN = auto()

    def __str__(self):
        return self.name


class ConflictingSemanticsError(RuntimeError):
    pass


class TensorSemantics(list):
    """ Semantics for a single input/output with at least known shape.
        See documentation at the top of the module. """

    def __init__(self, *axis_semantics: AxisSemantics):
        assert all(isinstance(s, AxisSemantics)
                   for s in axis_semantics), 'TensorSemantics excepts only AxisSemantics positional args'
        super().__init__(axis_semantics)

    def clone(self) -> 'TensorSemantics':
        return copy.deepcopy(self)

    def axis_by_semantics(self, axis_sem: AxisSemantics) -> int:
        if self.count(axis_sem) != 1:
            raise RuntimeError(
                f'Cannot retrieve axis by semantics {axis_sem} for {self} (either not found or has more than one)')
        return self.index(axis_sem)

    def has_unknown(self):
        return AxisSemantics.UNKNOWN in self

    # FIXME add tests
    @staticmethod
    def merge(ten_sem1: 'TensorSemantics', ten_sem2: 'TensorSemantics') -> 'TensorSemantics':
        assert isinstance(ten_sem1, TensorSemantics) and isinstance(ten_sem2, TensorSemantics)

        if len(ten_sem1) != len(ten_sem2):
            raise ConflictingSemanticsError(
                f'Cannot merge tensor semantics of different length: {ten_sem1} and {ten_sem2}')

        out = ten_sem1.clone()
        if ten_sem1 == ten_sem2:
            return out

        for i, (s1, s2) in enumerate(zip(ten_sem1, ten_sem2)):
            if s1 == s2:
                continue
            if s1 == AxisSemantics.UNKNOWN:
                out[i] = s2
            elif s2 == AxisSemantics.UNKNOWN:
                out[i] = s1
            else:
                raise ConflictingSemanticsError(f'Cannot merge conflicting tensor semantics: {ten_sem1} and {ten_sem2}')
        return out

    def __str__(self):
        return f"[{', '.join(map(str, self))}]"

    def __hash__(self):    # type: ignore
        return hash(str(self))


class Semantics(list):
    """ Semantics for all input/output tensors.
        See documentation at the top of the module. """

    def __init__(self, *tensor_semantics: Optional[TensorSemantics]):
        super().__init__(tensor_semantics)

    def clone(self) -> 'Semantics':
        return copy.deepcopy(self)

    def has_unknown(self):
        return None in self or any(ts.has_unknown() for ts in self)

    # FIXME add tests
    @staticmethod
    def merge(sem1: 'Semantics', sem2: 'Semantics'):
        assert isinstance(sem1, Semantics) and isinstance(sem2, Semantics)

        if len(sem1) != len(sem2):
            raise ConflictingSemanticsError(f'Cannot merge semantics of different length: {sem1} and {sem2}')

        out = sem1.clone()
        if sem1 == sem2:
            return out

        for i, (s1, s2) in enumerate(zip(sem1, sem2)):
            if s1 == s2:
                continue
            if s1 is None:
                out[i] = s2
            elif s2 is None:
                out[i] = s1
            else:
                try:
                    out[i] = TensorSemantics.merge(s1, s2)
                except ConflictingSemanticsError:
                    raise ConflictingSemanticsError(f'Failed to merge tensor {i} of semantics {sem1} and {sem2}')

        return out

    def __str__(self):
        return f"[{', '.join(map(str, self))}]"


data_tensor_semantics = {
    DataFormat.CHW: TensorSemantics(AxisSemantics.BATCH,
                                    AxisSemantics.CHANNELS,
                                    AxisSemantics.HEIGHT,
                                    AxisSemantics.WIDTH),
    DataFormat.HWC: TensorSemantics(AxisSemantics.BATCH,
                                    AxisSemantics.HEIGHT,
                                    AxisSemantics.WIDTH,
                                    AxisSemantics.CHANNELS)
}  # yapf: disable


class SemanticsHelper:

    def __init__(self, data_format: DataFormat):
        self.data_format = data_format

    def node_data_semantics(self) -> Semantics:
        """ Create semantics for a node with a single data input/output (data = same as network input) """
        return Semantics(self.data_tensor_semantics())

    def data_tensor_semantics(self) -> TensorSemantics:
        """ Create semantics for single data tensor """
        if self.data_format not in data_tensor_semantics:
            raise RuntimeError(f'Unexpected data format {self.data_format}')

        return data_tensor_semantics[self.data_format]

    def axis_by_semantics(self, axis_sem: AxisSemantics) -> int:
        """ Get index of axis corresponding to axis_sem """
        return self.data_tensor_semantics().index(axis_sem)

    def data_h_axis(self) -> int:
        """ Get index of axis corresponding to height """
        return self.axis_by_semantics(AxisSemantics.HEIGHT)

    def data_w_axis(self) -> int:
        """ Get index of axis corresponding to width """
        return self.axis_by_semantics(AxisSemantics.WIDTH)
