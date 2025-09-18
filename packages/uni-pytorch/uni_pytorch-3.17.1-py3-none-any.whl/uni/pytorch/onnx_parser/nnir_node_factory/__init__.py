# -------------------------------------------------------------------------------
# (c) Copyright 2022 Sony Semiconductor Israel, Ltd. All rights reserved.
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
Created on 10/13/22

@author: irenab
"""
from .base_factory import OnnxFactoryBase, validate_onnx

from .abs_factory import OnnxAbsToNnirNode
from .add_factory import OnnxAddToNnirNode
from .arg_factories import OnnxArgmaxToNnirNode
from .average_pool_factory import OnnxAveragePoolToNnirNode
from .batch_norm_factory import OnnxBatchNormToNnirNode
from .box_decode_factory import OnnxBoxDecodeToNnirNode
from .cast_factory import OnnxCastToNnirNode
from .clip_factory import OnnxClipToNnirNode
from .concat_factory import OnnxConcatToNnirNode
from .const_factory import OnnxConstToNnirNode
from .conv2d_factory import Conv2dOnnxFactory
from .conv2dtranspose_factory import Conv2dTransposeOnnxFactory
from .cos_factory import OnnxCosToNnirNode
from .exp_factory import OnnxExpToNnirNode
from .dummy_factories import OnnxDummyInputToNnirNode, OnnxDummyOutputToNnirNode
from .div_factory import OnnxDivToNnirNode
from .dropout_factory import OnnxDropoutToNnirNode
from .equal_factory import OnnxEqualToNnirNode
from .expand_factory import OnnxExpandToNnirNode
from .flatten_factory import OnnxFlattenToNnirNode
from .gather_factory import OnnxGatherToNnirNode
from .gather_elements_factory import OnnxGatherElementsToNnirNode
from .gelu_factory import OnnxGeluToNnirNode
from .gemm_factory import OnnxGemmToNnirNode
from .global_avg_pool_factory import OnnxGlobalAvgPoolToNnirNode
from .group_norm_factory import OnnxGroupNormToNnirNode
from .hard_sigmoid_factory import OnnxHardSigmoidToNnirNode
from .hard_swish_factory import OnnxHardSwishToNnirNode
from .identity_factory import OnnxIdentityToNnirNode
from .instance_norm_factory import OnnxInstanceNormToNnirNode
from .layer_norm_factory import OnnxLayerNormToNnirNode
from .leaky_relu_factory import OnnxLeakyReluToNnirNode
from .matmul_factory import OnnxMatMulToNnirNode
from .max_factory import OnnxMaxToNnirNode
from .max_pool_factory import OnnxMaxPoolToNnirNode
from .min_factory import OnnxMinToNnirNode
from .mul_factory import OnnxMulToNnirNode
from .multiclass_nms_factory import OnnxMultiClassNMSToNnirNode
from .multiclass_nms_factory_with_indices import OnnxMultiClassNMSWithIndicesToNnirNode
from .neg_factory import OnnxNegToNnirNode
from .output_factory import OnnxOutputToNnirNode
from .pad_factory import OnnxPadToNnirNode
from .placeholder_factory import OnnxPlaceholderToNnirNode
from .pow_factory import OnnxPowToNnirNode
from .reduce_factories import OnnxReduceMeanToNnirNode, OnnxReduceMaxToNnirNode, OnnxReduceSumToNnirNode
from .reduce_factories import OnnxReduceL2ToNnirNodeBase
from .relu_factory import OnnxReluToNnirNode
from .resize_factory import OnnxResizeToNnirNode
from .reshape_factory import OnnxReshapeToNnirNode
from .sigmoid_factory import OnnxSigmoidToNnirNode
from .sin_factory import OnnxSinToNnirNode
from .slice_factory import OnnxSliceToNnirNode
from .softmax_factory import OnnxSoftmaxNnirNode
from .split_factory import OnnxSplitNnirNode
from .squeeze_factory import OnnxSqueezeToNnirNode
from .sqrt_factory import OnnxSqrtToNnirNode
from .sub_factory import OnnxSubToNnirNode
from .unsqueeze_factory import OnnxUnSqueezeToNnirNode
from .tanh_factory import OnnxTanhToNnirNode
from .topk_factory import OnnxTopKToNnirNode
from .transpose_factory import OnnxTransposeToNnirNode
