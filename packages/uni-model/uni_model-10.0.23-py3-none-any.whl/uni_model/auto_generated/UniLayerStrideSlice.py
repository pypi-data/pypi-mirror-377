# -------------------------------------------------------------------------------
# (c) Copyright 2025 Sony Semiconductor Israel, Ltd. All rights reserved.
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

# This class is auto-generated in PythonGenerator of UniModel. Please don't change
from dataclasses import dataclass
import numpy as np
from typing import List, ClassVar
from uni_model.model.uni_layer import UniLayerBase, UniLayer
from uni_model.utils.immute import immute


@dataclass(frozen=True)
class _UniLayerBaseStrideSlice(UniLayerBase):
	begin: List[int]
	end: List[int]
	stride: List[int]
	begin_mask: int
	end_mask: int
	ellipsis_mask: int
	new_axis_mask: int
	shrink_axis_mask: int


@dataclass(frozen=True)
class UniLayerStrideSlice(UniLayer, _UniLayerBaseStrideSlice):
	op: ClassVar = "StrideSlice"
	output_names: ClassVar = [""]

	def __eq__(self, other):
		if self.name != other.name or self.begin != other.begin or self.end != other.end or self.stride != other.stride or self.begin_mask != other.begin_mask or self.end_mask != other.end_mask or self.ellipsis_mask != other.ellipsis_mask or self.new_axis_mask != other.new_axis_mask or self.shrink_axis_mask != other.shrink_axis_mask or self.out_shapes != other.out_shapes or self.out_dtypes != other.out_dtypes or self.history != other.history or any([v != other.extended_attr[k] if not isinstance(v, float) else not np.allclose(v, other.extended_attr[k]) for k, v in self.extended_attr.items()]):
			return False
		return True

	def __hash__(self):
		return hash((self.name, tuple(self.begin), tuple(self.end), tuple(self.stride), self.begin_mask, self.end_mask, self.ellipsis_mask, self.new_axis_mask, self.shrink_axis_mask, tuple(self.out_shapes), tuple(self.out_dtypes), tuple(self.history), immute(self.extended_attr)))


