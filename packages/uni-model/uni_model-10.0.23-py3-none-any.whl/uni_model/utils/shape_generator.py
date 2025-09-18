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
Created on 3/8/23

@author: zvikaa
'''
from typing import Iterable

from uni_model.auto_generated.EmptyShape import EmptyShape
from uni_model.auto_generated.Shape import Shape
from uni_model.auto_generated.ShapeImpl import ShapeImpl
from uni_model.validation.uni_model_exception import UniModelException


def shape_of(*elements: Iterable[int], neg_dim_allowed: bool = False) -> Shape:
    if len(elements) == 0:
        return EmptyShape()

    if neg_dim_allowed is False and any([e < 0 for e in elements]):
        raise UniModelException(message="Negative dimensions are not allowed")
    return ShapeImpl(list(elements))
