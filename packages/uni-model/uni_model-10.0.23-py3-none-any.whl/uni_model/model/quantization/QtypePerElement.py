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


from dataclasses import dataclass, field
from uni_model.auto_generated import Shape
import numpy as np
from uni_model.model.quantization.Qtype import Qtype
from typing import List
from uni_model.model.accuracy.min_max import MinMaxOpenEnded
from uni_model.validation.uni_model_exception import UniModelException


@dataclass(frozen=True)
class QtypePerElement(Qtype):
    value_n_bits: int
    min_maxes: List[MinMaxOpenEnded]
    _min_array: np.ndarray = field(default=None, init=False, repr=False)
    _max_array: np.ndarray = field(default=None, init=False, repr=False)
    _scale: np.ndarray = field(default=None, init=False, repr=False)
    _zero_point: np.ndarray = field(default=None, init=False, repr=False)

    def __eq__(self, other):
        if not self.value_n_bits == other.value_n_bits or not np.allclose(self._min_array,
                                                                          other._min_array) or not np.allclose(
                self._max_array, other._max_array):
            return False
        return True

    def validate_shapes(self, shape: Shape):
        if np.prod(shape.elements) == len(self.min_maxes):
            return None
        else:
            return f"shape {shape} product doesn't match given min max list with size {len(self.min_maxes)}"

    def __post_init__(self):
        if len(self.min_maxes) == 0:
            raise UniModelException(message="min_maxes mustn't be empty")
        object.__setattr__(self, '_min_array', np.array([mm.min for mm in self.min_maxes]))
        object.__setattr__(self, '_max_array', np.array([mm.max for mm in self.min_maxes]))
        object.__setattr__(self, '_scale', (self._max_array - self._min_array-(self._max_array - self._min_array)/(2**self.value_n_bits))/(2**self.value_n_bits - 1))
        object.__setattr__(self, '_zero_point', self._min_array / self._scale)

    def __hash__(self):
        return hash((self.value_n_bits, tuple(self.min_maxes)))

    def transform_to_fixed_point_repr(self, values: np.ndarray) -> np.ndarray:
        scale = self._scale.reshape(values.shape)
        zero_point = self._zero_point.reshape(values.shape)
        fixed_point_repr = np.round(values / scale - zero_point)
        fixed_point_repr = np.clip(fixed_point_repr, 0, 2 ** self.value_n_bits - 1).astype(np.int32)

        return fixed_point_repr

    def transform_from_fixed_point_repr(self, values: np.ndarray):
        scale = self._scale.reshape(values.shape)
        zero_point = self._zero_point.reshape(values.shape)
        float_values = (values + zero_point) * scale
        return float_values.astype(np.float32)

    def validate_fixed_point_repr(self, node_name: str, float_repr: np.ndarray, fixed_point_repr: np.ndarray):
        scale = self._scale.reshape(float_repr.shape)
        min_array = self._min_array.reshape(float_repr.shape)
        max_array = self._max_array.reshape(float_repr.shape)

        close_enough_mask = np.abs(
            np.clip(float_repr, min_array, max_array) - self.transform_from_fixed_point_repr(fixed_point_repr)) <= 0.1 * scale + self.eps
        self.validate_threshold(node_name, float_repr, close_enough_mask)
