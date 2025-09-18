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
'''
Created on 7/16/23

@author: zvikaa
'''

from uni_model.validation.error_codes import ErrorCodes
import numpy as np
from dataclasses import dataclass

from uni_model.validation.uni_model_exception import UniModelException


@dataclass
class MinMaxOpenEnded:
    min: float
    max: float

    def __hash__(self):
        return hash((np.float32(self.min), (np.float32(self.max))))

    def __str__(self):
        return f"[{self.min}..{self.max})"

    def __eq__(self, other):
        if not isinstance(other, MinMaxOpenEnded):
            return False
        if not np.isclose(self.min, other.min) or not np.isclose(self.max, other.max):
            return False
        return True

    def __contains__(self, item):
        return self.min <= item < self.max

    def scale_factor(self, nbits: int) -> float:
        return (self.max - self.min) / (2 ** nbits)

    @staticmethod
    def from_closed_ended(min: float, max: float, n_bits: int):
        scale = (max - min) / (2 ** n_bits - 1)
        new_max = max + scale
        return MinMaxOpenEnded(min, new_max)

    @staticmethod
    def from_open_positive_threshold(threshold: float):
        if threshold <= 0:
            raise UniModelException(ErrorCodes.TMBP, f"{ErrorCodes.TMBP.value}")
        return MinMaxOpenEnded(0, threshold)

    @staticmethod
    def from_open_symmetric_threshold(threshold: float):
        if threshold <= 0:
            raise UniModelException(ErrorCodes.TMBP, f"{ErrorCodes.TMBP.value}")
        return MinMaxOpenEnded(-threshold, threshold)
