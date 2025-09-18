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
from typing import List

import numpy as np
from uni_model.model.quantization.Qtype import Qtype
from uni_model.model.accuracy.const import _Const


@dataclass
class _QuantizedConst(_Const):
    fixed_point_repr: np.ndarray
    qtype: Qtype

    def __init__(self, fixed_point_repr: np.ndarray, qtype: Qtype):
        super(_QuantizedConst, self).__init__(self.calc_values(fixed_point_repr, qtype), qtype)
        self.fixed_point_repr = fixed_point_repr
        self.qtype = qtype

    @classmethod
    def calc_values(cls, fixed_point_repr: np.ndarray, qtype: Qtype) -> np.ndarray:
        return qtype.transform_from_fixed_point_repr(fixed_point_repr)
