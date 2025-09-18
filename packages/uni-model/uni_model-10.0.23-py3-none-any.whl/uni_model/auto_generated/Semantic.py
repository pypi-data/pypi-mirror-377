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
from enum import Enum


class Semantic(Enum):
	B = 0  # BATCH
	C = 1  # CHANNEL
	H = 2  # HEIGHT
	W = 3  # WIDTH
	AN = 4  # ANCHORS
	BX = 5  # BOXES
	KH = 6  # KERNEL_H
	KW = 7  # KERNEL_W
	CI = 8  # CHANNELS_IN
	CO = 9  # CHANNELS_OUT
	DT = 10  # DETECTIONS
	CS = 11  # CLASSES
	CH_GROUP = 12  # CHANNELS_PER_GROUP
	S = 13  # SCRATCH

