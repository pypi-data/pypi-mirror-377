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
Created on 9/18/23

@author: lotanw
"""
from .base_factory import validate_onnx
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.nnir_graph.nnir_nodes import Min
from .min_max_factory import MinMaxFactory


class OnnxMinToNnirNode(MinMaxFactory):
    """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#Min """

    @classmethod
    @validate_onnx(num_inputs=None, num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx=None) -> Min:
        cls.validate_num_inputs(graph_ctx, onnx_node)
        return Min(onnx_node.name)
