# -------------------------------------------------------------------------------
# (c) Copyright 2024 Sony Semiconductor Israel, Ltd. All rights reserved.
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
'''
Created on 9/16/24

@author: zvikaa
'''
from dataclasses import dataclass
import numpy as np

from uni_model.model.quantization.Dtype import Dtype
from uni_model.model.quantization.Dfloat import Dfloat
from uni_model.model.quantization.Qtype import Qtype


@dataclass
class _Const:
    values: np.ndarray
    dtype: Dtype

    def to_quantized_const(self):
        if isinstance(self.dtype, Dfloat):
            raise Exception("You cannot convert dfloat const to quantized const")
        elif isinstance(self.dtype, Qtype):
            from uni_model.model.accuracy.quantized_const import _QuantizedConst
            return _QuantizedConst(self.dtype.transform_to_fixed_point_repr(self.values), self.dtype)

    def compact(self):
        if isinstance(self.dtype, Qtype):
            return self.to_quantized_const()
        else:
            return self
