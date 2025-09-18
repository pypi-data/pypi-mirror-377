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
Created on 10/19/22

@author: irenab
"""
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.nnir_graph.nnir_nodes import Reshape
from uni.common.core.node_history import NodeHistory
from uni.common.core.multigraph.node_graph_api import NodeGraphContext


class OnnxFlattenToNnirNode(OnnxFactoryBase):
    # supports axis == 0, in ONNX the result of such flatten for shape (x_0, ... , x_n) is (1, x_0* ... *x_n).
    # supports axis == 1, trivial case where batch dim is unaffected.
    # supports axis == n > 1 as long as x_0 == ... == x_n-1 == 1. In such cases the batch dim is unaffected as well.

    @classmethod
    @validate_onnx(num_inputs=1, num_outputs=1, attrs=[], optional_attrs=['axis'])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> Reshape:
        """  https://github.com/onnx/onnx/blob/main/docs/Operators.md#Flatten
             Always creates 2d output. All dimensions up to axis-1 are flattened into 1st dim,
             all dimensions starting from axis are flattened into the 2nd dims.
        """
        target_shape = graph_ctx.get_out_shapes()[0]
        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='Flatten -> Reshape')
        return Reshape(onnx_node.name, target_shape=target_shape, history=history)
