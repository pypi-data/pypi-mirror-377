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
"""
Created on 3/16/23

@author: irenab
"""
from typing import Dict, Union, Type

from uni.common.parsers.base_reader import MetaOpType
from .nnir_node_factory.mct_quantizers_nodes import ActivationPOTQuantizerToNnirNode, WeightsPOTQuantizerToNnirNode, \
    WeightsSymmetricQuantizerToNnirNode, WeightsLutSymmetricQuantizerToNnirNode, WeightsLutPOTQuantizerToNnirNode
from .onnx_mct_reader_helper import OnnxMctQWeightsQuantizer
from .onnx_reader_helper import OnnxOpType
from .nnir_node_factory import *    # noqa: F403

OnnxOpT = Union[str, MetaOpType, OnnxOpType]
NodeFactoryT = Dict[OnnxOpT, Type[OnnxFactoryBase]]

onnx_op_factory: NodeFactoryT = {
    'Abs': OnnxAbsToNnirNode,
    'Add': OnnxAddToNnirNode,
    'ArgMax': OnnxArgmaxToNnirNode,
    'AveragePool': OnnxAveragePoolToNnirNode,
    'Cast': OnnxCastToNnirNode,
    'Clip': OnnxClipToNnirNode,
    'Conv': Conv2dOnnxFactory,
    'Concat': OnnxConcatToNnirNode,
    'ConvTranspose': Conv2dTransposeOnnxFactory,
    'Cos': OnnxCosToNnirNode,
    'Div': OnnxDivToNnirNode,
    'Dropout': OnnxDropoutToNnirNode,
    'Equal': OnnxEqualToNnirNode,
    'Exp': OnnxExpToNnirNode,
    "Expand": OnnxExpandToNnirNode,
    'Flatten': OnnxFlattenToNnirNode,
    'Gather': OnnxGatherToNnirNode,
    'GatherElements': OnnxGatherElementsToNnirNode,
    'Gelu': OnnxGeluToNnirNode,
    'Gemm': OnnxGemmToNnirNode,
    'GlobalAveragePool': OnnxGlobalAvgPoolToNnirNode,
    'GroupNormalization': OnnxGroupNormToNnirNode,
    'HardSigmoid': OnnxHardSigmoidToNnirNode,
    'HardSwish': OnnxHardSwishToNnirNode,
    'InstanceNormalization': OnnxInstanceNormToNnirNode,
    'LayerNormalization': OnnxLayerNormToNnirNode,
    'LeakyRelu': OnnxLeakyReluToNnirNode,
    'MatMul': OnnxMatMulToNnirNode,
    'Max': OnnxMaxToNnirNode,
    'MaxPool': OnnxMaxPoolToNnirNode,
    'Min': OnnxMinToNnirNode,
    'Mul': OnnxMulToNnirNode,
    'Neg': OnnxNegToNnirNode,
    'Pad': OnnxPadToNnirNode,
    'Pow': OnnxPowToNnirNode,
    'ReduceL2': OnnxReduceL2ToNnirNodeBase,
    'ReduceMax': OnnxReduceMaxToNnirNode,
    'ReduceMean': OnnxReduceMeanToNnirNode,
    'ReduceSum': OnnxReduceSumToNnirNode,
    'Relu': OnnxReluToNnirNode,
    'Reshape': OnnxReshapeToNnirNode,
    'Resize': OnnxResizeToNnirNode,
    'Sigmoid': OnnxSigmoidToNnirNode,
    'Sin': OnnxSinToNnirNode,
    'Slice': OnnxSliceToNnirNode,
    'Softmax': OnnxSoftmaxNnirNode,
    'Split': OnnxSplitNnirNode,
    'Sqrt': OnnxSqrtToNnirNode,
    'Squeeze': OnnxSqueezeToNnirNode,
    'Sub': OnnxSubToNnirNode,
    'Unsqueeze': OnnxUnSqueezeToNnirNode,
    'Tanh': OnnxTanhToNnirNode,
    'TopK': OnnxTopKToNnirNode,
    'Transpose': OnnxTransposeToNnirNode,
    'BatchNormalization': OnnxBatchNormToNnirNode,

    OnnxOpType.Identity: OnnxIdentityToNnirNode,
    OnnxOpType.Constant: OnnxConstToNnirNode,

    MetaOpType.Placeholder: OnnxPlaceholderToNnirNode,
    MetaOpType.Output: OnnxOutputToNnirNode,
    MetaOpType.DummyInput: OnnxDummyInputToNnirNode,
    MetaOpType.DummyOutput: OnnxDummyOutputToNnirNode,

    "ActivationPOTQuantizer": ActivationPOTQuantizerToNnirNode,

    OnnxMctQWeightsQuantizer.WeightsPOTQuantizer: WeightsPOTQuantizerToNnirNode,
    OnnxMctQWeightsQuantizer.WeightsSymmetricQuantizer: WeightsSymmetricQuantizerToNnirNode,
    OnnxMctQWeightsQuantizer.WeightsLUTSymmetricQuantizer: WeightsLutSymmetricQuantizerToNnirNode,
    OnnxMctQWeightsQuantizer.WeightsLUTPOTQuantizer: WeightsLutPOTQuantizerToNnirNode,

    'FasterRCNNBoxDecode': OnnxBoxDecodeToNnirNode,
    'MultiClassNMS': OnnxMultiClassNMSToNnirNode,
    'MultiClassNMSWithIndices': OnnxMultiClassNMSWithIndicesToNnirNode,
}  # yapf: disable
