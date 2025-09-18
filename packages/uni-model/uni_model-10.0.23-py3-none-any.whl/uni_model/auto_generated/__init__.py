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
from uni_model.auto_generated.Shape import Shape
from uni_model.auto_generated.UniLayerReduce import UniLayerReduce
from uni_model.auto_generated.UniPadding import UniPadding
from uni_model.auto_generated.UniSliceConfig import UniSliceConfig
from uni_model.auto_generated.UniWindow import UniWindow
from uni_model.auto_generated.EmptyShape import EmptyShape
from uni_model.auto_generated.ShapeImpl import ShapeImpl
from uni_model.auto_generated.TensorDesc import TensorDesc
from uni_model.auto_generated.DataFormat import DataFormat
from uni_model.auto_generated.PlaceholderDtype import PlaceholderDtype
from uni_model.auto_generated.ResizeMethod import ResizeMethod
from uni_model.auto_generated.Semantic import Semantic
from uni_model.auto_generated.UniLayerAbs import UniLayerAbs
from uni_model.auto_generated.UniLayerArgMax import UniLayerArgMax
from uni_model.auto_generated.UniLayerBatchNorm import UniLayerBatchNorm
from uni_model.auto_generated.UniLayerBiasAdd import UniLayerBiasAdd
from uni_model.auto_generated.UniLayerBinary import UniLayerBinary
from uni_model.auto_generated.UniLayerBroadcast import UniLayerBroadcast
from uni_model.auto_generated.UniLayerCast import UniLayerCast
from uni_model.auto_generated.UniLayerClip import UniLayerClip
from uni_model.auto_generated.UniLayerConcat import UniLayerConcat
from uni_model.auto_generated.UniLayerCos import UniLayerCos
from uni_model.auto_generated.UniLayerDecode import UniLayerDecode
from uni_model.auto_generated.UniLayerExp import UniLayerExp
from uni_model.auto_generated.UniLayerExpandDims import UniLayerExpandDims
from uni_model.auto_generated.UniLayerFasterRCNNBoxDecode import UniLayerFasterRCNNBoxDecode
from uni_model.auto_generated.UniLayerFusedBatchNorm import UniLayerFusedBatchNorm
from uni_model.auto_generated.UniLayerGelu import UniLayerGelu
from uni_model.auto_generated.UniLayerGroupNorm import UniLayerGroupNorm
from uni_model.auto_generated.UniLayerHardSigmoid import UniLayerHardSigmoid
from uni_model.auto_generated.UniLayerHardSwish import UniLayerHardSwish
from uni_model.auto_generated.UniLayerIdentity import UniLayerIdentity
from uni_model.auto_generated.UniLayerLayerNorm import UniLayerLayerNorm
from uni_model.auto_generated.UniLayerMatMulBias import UniLayerMatMulBias
from uni_model.auto_generated.UniLayerMatmul import UniLayerMatmul
from uni_model.auto_generated.UniLayerMultiClassNonMaxSuppression import UniLayerMultiClassNonMaxSuppression
from uni_model.auto_generated.UniLayerNeg import UniLayerNeg
from uni_model.auto_generated.UniLayerNorm import UniLayerNorm
from uni_model.auto_generated.UniLayerOutput import UniLayerOutput
from uni_model.auto_generated.UniLayerPRelu import UniLayerPRelu
from uni_model.auto_generated.UniLayerPad import UniLayerPad
from uni_model.auto_generated.UniLayerReduceMax import UniLayerReduceMax
from uni_model.auto_generated.UniLayerReduceMean import UniLayerReduceMean
from uni_model.auto_generated.UniLayerReduceSum import UniLayerReduceSum
from uni_model.auto_generated.UniLayerRelu import UniLayerRelu
from uni_model.auto_generated.UniLayerReshapeStructure import UniLayerReshapeStructure
from uni_model.auto_generated.UniLayerRsqrt import UniLayerRsqrt
from uni_model.auto_generated.UniLayerSigmoid import UniLayerSigmoid
from uni_model.auto_generated.UniLayerSin import UniLayerSin
from uni_model.auto_generated.UniLayerSlice import UniLayerSlice
from uni_model.auto_generated.UniLayerSoftmax import UniLayerSoftmax
from uni_model.auto_generated.UniLayerSources import UniLayerSources
from uni_model.auto_generated.UniLayerSplitStructure import UniLayerSplitStructure
from uni_model.auto_generated.UniLayerSplitVStructure import UniLayerSplitVStructure
from uni_model.auto_generated.UniLayerSqrt import UniLayerSqrt
from uni_model.auto_generated.UniLayerSqueeze import UniLayerSqueeze
from uni_model.auto_generated.UniLayerStack import UniLayerStack
from uni_model.auto_generated.UniLayerStrideSlice import UniLayerStrideSlice
from uni_model.auto_generated.UniLayerSwish import UniLayerSwish
from uni_model.auto_generated.UniLayerTanh import UniLayerTanh
from uni_model.auto_generated.UniLayerTopK import UniLayerTopK
from uni_model.auto_generated.UniLayerTopKGather import UniLayerTopKGather
from uni_model.auto_generated.UniLayerTranspose import UniLayerTranspose
from uni_model.auto_generated.UniLayerUnstack import UniLayerUnstack
from uni_model.auto_generated.UniLayerWildcard import UniLayerWildcard
from uni_model.auto_generated.UniLayerAvgPool import UniLayerAvgPool
from uni_model.auto_generated.UniLayerMaxPool import UniLayerMaxPool
from uni_model.auto_generated.UniLayerResize import UniLayerResize
from uni_model.auto_generated.UniLayerUpSampling2D import UniLayerUpSampling2D
from uni_model.auto_generated.Layout import Layout
from uni_model.auto_generated.UniLayerAdd import UniLayerAdd
from uni_model.auto_generated.UniLayerDiv import UniLayerDiv
from uni_model.auto_generated.UniLayerEqual import UniLayerEqual
from uni_model.auto_generated.UniLayerMax import UniLayerMax
from uni_model.auto_generated.UniLayerMin import UniLayerMin
from uni_model.auto_generated.UniLayerMul import UniLayerMul
from uni_model.auto_generated.UniLayerSub import UniLayerSub
from uni_model.auto_generated.UniLayerRelu6 import UniLayerRelu6
from uni_model.auto_generated.UniLayerConstStructure import UniLayerConstStructure
from uni_model.auto_generated.UniLayerPlaceholder import UniLayerPlaceholder
from uni_model.auto_generated.UniLayerConv2D import UniLayerConv2D
from uni_model.auto_generated.UniLayerConv2DTranspose import UniLayerConv2DTranspose
from uni_model.auto_generated.UniLayerFullyConnected import UniLayerFullyConnected
