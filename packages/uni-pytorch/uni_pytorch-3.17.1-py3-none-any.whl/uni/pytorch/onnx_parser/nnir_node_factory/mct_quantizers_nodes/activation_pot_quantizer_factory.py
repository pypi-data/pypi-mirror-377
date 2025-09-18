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
from uni.common.core.nnir_graph.nnir_nodes import Quant
from uni.common.core.nnir_graph.quant_info import SymmetricQuantInfo
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import validate_onnx
from . import OnnxMctFactoryBase


class ActivationPOTQuantizerToNnirNode(OnnxMctFactoryBase):

    @classmethod
    @validate_onnx(num_inputs=1, num_outputs=1, attrs=['mctq_version', 'num_bits', 'signed', 'threshold'])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx) -> Quant:
        threshold = onnx_node.get_attr('threshold')
        signed = onnx_node.get_attr('signed')
        num_bits = onnx_node.get_attr('num_bits')
        quant_info = SymmetricQuantInfo(value_n_bits=num_bits, threshold=threshold, signed=signed)
        return Quant(name=onnx_node.name, quant_info=quant_info)
