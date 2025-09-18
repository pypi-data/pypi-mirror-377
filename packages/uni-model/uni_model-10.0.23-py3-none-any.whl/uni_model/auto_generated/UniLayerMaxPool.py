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
from uni_model.auto_generated.DataFormat import DataFormat
from typing import ClassVar
from uni_model.model.uni_layer import UniLayerBase, UniLayer
from uni_model.utils.immute import immute


@dataclass(frozen=True)
class _UniLayerBaseMaxPool(UniLayerBase):
	k_h: int
	k_w: int
	s_h: int
	s_w: int
	p_h_before: int
	p_h_after: int
	p_w_before: int
	p_w_after: int
	data_format: DataFormat


@dataclass(frozen=True)
class UniLayerMaxPool(UniLayer, _UniLayerBaseMaxPool):
	op: ClassVar = "MaxPool"
	input_names: ClassVar = ["input"]
	output_names: ClassVar = [""]

	def __eq__(self, other):
		if self.name != other.name or self.k_h != other.k_h or self.k_w != other.k_w or self.s_h != other.s_h or self.s_w != other.s_w or self.p_h_before != other.p_h_before or self.p_h_after != other.p_h_after or self.p_w_before != other.p_w_before or self.p_w_after != other.p_w_after or self.out_shapes != other.out_shapes or self.out_dtypes != other.out_dtypes or self.data_format != other.data_format or self.history != other.history or any([v != other.extended_attr[k] if not isinstance(v, float) else not np.allclose(v, other.extended_attr[k]) for k, v in self.extended_attr.items()]):
			return False
		return True

	def __hash__(self):
		return hash((self.name, self.k_h, self.k_w, self.s_h, self.s_w, self.p_h_before, self.p_h_after, self.p_w_before, self.p_w_after, tuple(self.out_shapes), tuple(self.out_dtypes), self.data_format, tuple(self.history), immute(self.extended_attr)))


