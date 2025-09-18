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
Created on 2/15/23

@author: zvikaa
'''
from typing import List, Dict, Any

import numpy as np

from uni_model.validation.uni_model_exception import UniModelException
from uni_model.model.quantization.Dfloat import Dfloat
from uni_model.auto_generated import Shape
from uni_model.auto_generated.ShapeImpl import ShapeImpl
from uni_model.model.quantization.Dtype import Dtype
from uni_model.model.behavioral.UniLayerConst import UniLayerConst
from uni_model.validation.error_codes import ErrorCodes


def create_const_with_data(name: str, float_data: np.ndarray, dtype: Dtype = Dfloat(32),
                           history: List[str] = None, attr: Dict[str, Any] = None) -> UniLayerConst:
    if float_data.dtype != np.float32:
        raise UniModelException(ErrorCodes.FMB32, f"{ErrorCodes.FMB32.value}")
    shape = ShapeImpl(list(float_data.shape))
    if not shape:
        shape = ShapeImpl([1])
        float_data = (float_data.item())
    if history is None:
        history = []
    if attr is None:
        attr = {}
    return UniLayerConst(name, float_data, np.array([]), [shape], [dtype], history, attr)


def _create_const_with_fixed_point_repr_data(name: str, fixed_point_repr: np.ndarray, dtype: Dtype,
                                             out_shapes: List[Shape],
                                             history: List[str] = None, attr: Dict[str, Any] = None) -> UniLayerConst:
    if out_shapes is None:
        out_shapes = []
    if history is None:
        history = []
    if attr is None:
        attr = {}

    return UniLayerConst(name, np.array([]), fixed_point_repr, out_shapes, [dtype], history, attr)
