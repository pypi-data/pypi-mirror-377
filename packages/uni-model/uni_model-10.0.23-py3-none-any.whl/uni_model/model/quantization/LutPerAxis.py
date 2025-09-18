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
import numpy as np

from uni_model import UniModelException
from uni_model.model.quantization.Lut import Lut
from typing import List
from uni_model.model.accuracy.min_max import MinMaxOpenEnded


@dataclass(frozen=True)
class LutPerAxis(Lut):
    axis: int
    min_maxes: List[MinMaxOpenEnded]
    _min_vals: np.ndarray = field(default=None, init=False, repr=False)
    _max_vals: np.ndarray = field(default=None, init=False, repr=False)

    def __init__(self, value_n_bits: int, table: List[float], table_n_bits: int, axis: int, min_maxes: List[MinMaxOpenEnded],
                 normalized_min: float = -1, normalized_max: float = 1):
        object.__setattr__(self, "value_n_bits", value_n_bits)
        object.__setattr__(self, "table", table)
        object.__setattr__(self, "table_n_bits", table_n_bits)
        object.__setattr__(self, "axis", axis)
        object.__setattr__(self, "min_maxes", min_maxes)
        object.__setattr__(self, "normalized_min", normalized_min)
        object.__setattr__(self, "normalized_max", normalized_max)
        self.__post_init__()

    def __post_init__(self):
        super().__post_init__()

    def __eq__(self, other):
        if self.value_n_bits != other.value_n_bits or not np.allclose(self.table,
                                                                      other.table) or self.table_n_bits != other.table_n_bits or self.axis != other.axis or self.min_maxes != other.min_maxes:
            return False
        return True

    def __hash__(self):
        return hash((self.value_n_bits, tuple(np.array(self.table, dtype='float32')), self.table_n_bits, self.axis,
                     tuple(self.min_maxes)))

    def __post_init__(self):
        super().__post_init__()
        if len(self.min_maxes) == 0:
            raise UniModelException(message="min_maxes mustn't be empty")
        object.__setattr__(self, '_min_vals', np.array([mm.min for mm in self.min_maxes]).astype(np.float32))
        object.__setattr__(self, '_max_vals', np.array([mm.max for mm in self.min_maxes]).astype(np.float32))

    def _expand_min_max(self, values: np.ndarray, dim: int):
        min_val_expanded = np.array(self._min_vals).reshape([-1 if i == dim else 1 for i in range(values.ndim)])
        max_val_expanded = np.array(self._max_vals).reshape([-1 if i == dim else 1 for i in range(values.ndim)])
        return min_val_expanded, max_val_expanded

    def transform_to_fixed_point_repr(self, values: np.ndarray) -> np.ndarray:
        dim = values.ndim + self.axis if self.axis < 0 else self.axis
        # moving values to the normalized values
        min_val_expanded, max_val_expanded = self._expand_min_max(values, dim)
        normalized_values = (values - min_val_expanded) * (self.normalized_max-self.normalized_min) / (max_val_expanded - min_val_expanded) + self.normalized_min
        differences = np.abs(normalized_values[..., None] - self._table_as_np)
        fixed_point_repr = np.argmin(differences, axis=-1)
        return fixed_point_repr

    def transform_from_fixed_point_repr(self, values: np.ndarray):
        normalized = self._table_as_np[values]
        dim = values.ndim + self.axis if self.axis < 0 else self.axis
        min_val_expanded, max_val_expanded = self._expand_min_max(values, dim)
        denormalized = (normalized - self.normalized_min) * (max_val_expanded - min_val_expanded)/(self.normalized_max-self.normalized_min) + min_val_expanded
        return denormalized.astype(np.float32)

    def validate_fixed_point_repr(self, node_name: str, float_repr: np.ndarray, fixed_point_repr: np.ndarray):
        dim = float_repr.ndim + self.axis if self.axis < 0 else self.axis
        dequantized = self.transform_from_fixed_point_repr(fixed_point_repr)
        min_val_expanded, max_val_expanded = self._expand_min_max(float_repr, dim)
        close_enough_mask = np.abs(dequantized - float_repr) <= 0.1 * (
                max_val_expanded - min_val_expanded) / (2 ** self.value_n_bits) + self.eps
        self.validate_threshold(node_name, float_repr, close_enough_mask)
