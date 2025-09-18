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

from uni_model.validation.validation_cfg import ValidationCfg
from uni_model.model.quantization.Qtype import Qtype
from uni_model.model.accuracy.min_max import MinMaxOpenEnded
import numpy as np
from uni_model.validation.error_builder import ErrorBuilder


@dataclass(frozen=True)
class QtypePerTensor(Qtype):
    value_n_bits: int
    min_max: MinMaxOpenEnded
    _scale: float = field(default=None, init=False, repr=False)
    _zero_point: float = field(default=None, init=False, repr=False)

    def __post_init__(self):
        object.__setattr__(self, '_scale', (self.min_max.max - self.min_max.min-(self.min_max.max - self.min_max.min)/(2**self.value_n_bits))/(2**self.value_n_bits - 1))
        object.__setattr__(self, '_zero_point', self.min_max.min / self._scale)

    def __hash__(self):
        return hash((self.value_n_bits, self.min_max))

    def transform_to_fixed_point_repr(self, values: np.ndarray)-> np.ndarray:
        fixed_point_repr = np.round(values/self._scale - self._zero_point)
        fixed_point_repr = np.clip(fixed_point_repr, 0, 2**self.value_n_bits-1).astype(np.int32)
        return fixed_point_repr

    def transform_from_fixed_point_repr(self, values: np.ndarray):
        float_values = (values + self._zero_point) * self._scale
        return float_values.astype(np.float32)

    def validate_fixed_point_repr(self, node_name: str, float_repr: np.ndarray, fixed_point_repr: np.ndarray):
        close_enough_mask = np.abs(np.clip(float_repr, self.min_max.min, self.min_max.max) - self.transform_from_fixed_point_repr(
            fixed_point_repr)) <= 0.1 * self._scale + self.eps
        self.validate_threshold(node_name, float_repr, close_enough_mask)


