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
Created on 11/16/22

@author: irenab
"""
from uni.common.core.nnir_graph import TensorSemantics, AxisSemantics
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.multigraph.node_graph_api import NodeGraphContext
from uni.common.core.nnir_graph.nnir_nodes import FullyConnected, Matmul
from uni.common.core.error.util import OpInputErrorInfo, raise_op_error
from uni.common.core.node_history import NodeHistory


class OnnxMatMulToNnirNode(OnnxFactoryBase):
    error_const_first_input = 'Only dynamic first input is supported'
    error_const_second_input = ('When the second input is const,'
                                ' its shape must be (Cin, Cout) (originated from fully connected layer).')

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext):
        a_input, b_input = graph_ctx.get_in_nodes()    # type: (OnnxMetaNode, OnnxMetaNode)
        a_shape, b_shape = graph_ctx.get_in_shapes()

        a_is_const = a_input.is_const(check_quant=True)
        b_is_const = b_input.is_const(check_quant=True)
        is_fc = b_is_const and len(b_shape) == 2

        errors = []
        if a_is_const:
            errors.append(OpInputErrorInfo(input_index=0, input_name=a_input.name, reason=cls.error_const_first_input))
        if b_is_const and len(b_shape) != 2:
            errors.append(OpInputErrorInfo(input_index=1, input_name=b_input.name, reason=cls.error_const_second_input))
        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

        if is_fc:
            node, request = cls._get_fc(graph_ctx, onnx_node)
        else:
            node, request = cls._get_matmul(onnx_node)
        return node, request

    @classmethod
    def _get_fc(cls, graph_ctx, onnx_node):
        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='MatMul with const -> FullyConnected')
        node = FullyConnected(onnx_node.name, history=history)
        node.weight_semantics = TensorSemantics(AxisSemantics.IN_CHANNELS, AxisSemantics.OUT_CHANNELS)
        has_bias, (out_channels, _), _ = node.validate_and_query_weights(graph_ctx.get_in_shapes(),
                                                                         node.weight_semantics,
                                                                         infer_kernel_size=False)
        request = None if has_bias else node.request_add_zero_bias(node.name, out_channels)
        return node, request

    @classmethod
    def _get_matmul(cls, onnx_node):
        history = NodeHistory(cls.onnx_op_info(onnx_node))
        node = Matmul(onnx_node.name, history=history, transpose_a=False, transpose_b=False)
        return node, None
