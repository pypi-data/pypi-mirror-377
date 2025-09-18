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
from uni_model.model.quantization.Qtype import Qtype
from typing import List
from uni_model.model.accuracy.min_max import MinMaxOpenEnded
from uni_model.validation.uni_model_exception import UniModelException
import numpy as np


@dataclass(frozen=True)
class QtypePerAxis(Qtype):
	value_n_bits: int 
	axis: int 
	min_maxes: List[MinMaxOpenEnded]
	_min_vals: np.ndarray = field(default=None, init=False, repr=False)
	_max_vals: np.ndarray = field(default=None, init=False, repr=False)
	_scale: np.ndarray = field(default=None, init=False, repr=False)
	_zero_point: np.ndarray = field(default=None, init=False, repr=False)

	def __eq__(self, other):
		if self.value_n_bits != other.value_n_bits or self.axis != other.axis \
				or not (np.allclose(self._min_vals, other._min_vals)) or not (np.allclose(self._max_vals, other._max_vals)):
			return False
		return True
	def validate_shapes(self, shape: Shape):
		size = len(shape.elements)
		dim = self.axis if self.axis >= 0 else size + self.axis
		if dim not in range(size):
			return f"axis {self.axis} is not in the range of shapes {size}"
		if shape.elements[self.axis] == len(self.min_maxes):
			return None
		else:
			return f"shape {shape} in axis {self.axis} doesn't match given min max list with size {len(self.min_maxes)}"

	def __post_init__(self):
		if len(self.min_maxes) == 0:
			raise UniModelException(message="min_maxes mustn't be empty")
		object.__setattr__(self, '_min_vals', np.array([mm.min for mm in self.min_maxes]))
		object.__setattr__(self, '_max_vals', np.array([mm.max for mm in self.min_maxes]))
		object.__setattr__(self, '_scale', (self._max_vals - self._min_vals-(self._max_vals - self._min_vals)/(2**self.value_n_bits))/(2**self.value_n_bits - 1))
		object.__setattr__(self, '_zero_point', self._min_vals / self._scale)

	def __hash__(self):
		return hash((self.value_n_bits, self.axis, tuple(self.min_maxes)))

	def _get_shape_for_axis(self, values: np.ndarray, replace_with_axis=False):
		dim = values.ndim + self.axis if self.axis < 0 else self.axis
		shape_for_axis = [1] * values.ndim
		if replace_with_axis:
			shape_for_axis[dim] = values.shape[dim]
		else:
			shape_for_axis[dim] = -1

		return shape_for_axis

	def transform_to_fixed_point_repr(self, values: np.ndarray)-> np.ndarray:
		shape_for_axis = self._get_shape_for_axis(values)
		scale = self._scale.reshape(shape_for_axis)
		zero_point = self._zero_point.reshape(shape_for_axis)

		fixed_point_repr = np.round(values/scale - zero_point)
		fixed_point_repr = np.clip(fixed_point_repr, 0, 2**self.value_n_bits - 1).astype(np.int32)

		return fixed_point_repr

	def transform_from_fixed_point_repr(self, values: np.ndarray):
		shape_for_axis = self._get_shape_for_axis(values)
		scale = self._scale.reshape(shape_for_axis)
		zero_point = self._zero_point.reshape(shape_for_axis)

		float_values = (values + zero_point) * scale
		return float_values.astype(np.float32)

	def validate_fixed_point_repr(self, node_name: str, float_repr: np.ndarray, fixed_point_repr: np.ndarray):
		shape_for_axis = self._get_shape_for_axis(float_repr)
		min_reshaped = self._min_vals.reshape(shape_for_axis)
		max_reshaped = self._max_vals.reshape(shape_for_axis)
		scale = self._scale.reshape(shape_for_axis)
		close_enough_mask = np.abs(
			np.clip(float_repr, min_reshaped, max_reshaped) - self.transform_from_fixed_point_repr(fixed_point_repr)) <= 0.1 * scale + self.eps
		self.validate_threshold(node_name, float_repr, close_enough_mask)
