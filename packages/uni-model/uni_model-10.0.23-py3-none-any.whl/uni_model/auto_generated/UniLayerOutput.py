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
from dataclasses import dataclass, field
import numpy as np
from typing import ClassVar, List
from uni_model.model.uni_layer import UniLayerBase, UniLayer
from uni_model.model.quantization.Dtype import Dtype
from uni_model.auto_generated.Shape import Shape
from uni_model.utils.immute import immute


@dataclass(frozen=True)
class _UniLayerBaseOutput(UniLayerBase):
	ordinal: int


@dataclass(frozen=True)
class UniLayerOutput(UniLayer, _UniLayerBaseOutput):
	op: ClassVar = "Output"
	out_dtypes: List[Dtype] = field(default_factory=list, init=False)
	out_shapes: List[Shape] = field(default_factory=list, init=False)
	_valid_output_range: ClassVar = range(0, 1)

	def __eq__(self, other):
		if self.name != other.name or self.ordinal != other.ordinal or self.history != other.history or any([v != other.extended_attr[k] if not isinstance(v, float) else not np.allclose(v, other.extended_attr[k]) for k, v in self.extended_attr.items()]):
			return False
		return True

	def __hash__(self):
		return hash((self.name, self.ordinal, tuple(self.history), immute(self.extended_attr)))


