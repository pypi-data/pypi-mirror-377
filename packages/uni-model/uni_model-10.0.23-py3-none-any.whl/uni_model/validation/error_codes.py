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
Created on 1/17/23

@author: zvikaa
'''
from enum import Enum


class ErrorCodes(Enum):
    LNMBU = "Layer name must be unique"
    EMBU = "Edge must be unique"
    GIMBU = "Graph id must be unique"
    ENMBIG = "Edge nodes must be in graph"
    CIDMBIN = "Const fixed_point_repr data must fit in given nBits range"
    TMBP = "Threshold must be positive"
    LMBIR = "Lut table values must be in range [-1, 1)"
    LTSR = "Lut table size must be up to 2^tableNBits"
    MCF = "Missing const file"
    QF = "Given value cannot be specified to an index in this qtype"
    LNVMMIR = "Lut normalized values must match in given range"
    FMB32 = "Numpy array dtype must be np.float32"
