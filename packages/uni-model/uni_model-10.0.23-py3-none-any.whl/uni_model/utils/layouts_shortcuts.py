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
Created on 2/14/23

@author: zvikaa
'''
from uni_model.auto_generated.Layout import Layout
from uni_model.auto_generated.Semantic import Semantic


def uni_layout_generator(*semantics) -> Layout:
    return Layout(list(semantics))

BCHW = uni_layout_generator(Semantic.B, Semantic.C, Semantic.H, Semantic.W)
BHWC = uni_layout_generator(Semantic.B, Semantic.H, Semantic.W, Semantic.C)

