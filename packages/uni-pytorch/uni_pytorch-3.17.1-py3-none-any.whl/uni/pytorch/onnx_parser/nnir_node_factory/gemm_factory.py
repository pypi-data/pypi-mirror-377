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
from typing import Tuple, Optional, List

import numpy as np

from uni.common.core.nnir_graph import TensorSemantics, AxisSemantics
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeGraphContext, ConstNodeCfg
from uni.common.core.nnir_graph.nnir_nodes import FullyConnected
from uni.common.core.error.util import raise_op_error, supported_vals_msg
from uni.common.core.error.defs import OpInputErrorInfo, ParamErrorInfo, ErrorInfo
from uni.common.core.node_history import NodeHistory


class OnnxGemmToNnirNode(OnnxFactoryBase):
    error_first_input = 'Only dynamic first input is supported'
    error_second_input = 'Only const second input is supported (originated from fully connected)'
    supported_factor = 1.
    supported_transpose_a = [0]
    error_invalid_factor = supported_vals_msg([supported_factor])
    error_invalid_transpose_a = supported_vals_msg(supported_transpose_a)

    @classmethod
    @validate_onnx(num_inputs=[2, 3], num_outputs=1, attrs=[], optional_attrs=['alpha', 'beta', 'transA', 'transB'])
    def from_onnx(cls, onnx_node: OnnxMetaNode,
                  graph_ctx: NodeGraphContext) -> Tuple[FullyConnected, Optional[GraphRequest]]:
        """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#Gemm """
        errors: List[ErrorInfo] = []
        input_a, input_b = graph_ctx.get_in_nodes()[:2]    # type: Tuple[OnnxMetaNode, OnnxMetaNode]
        input_a_name, input_b_name = [n.name for n in graph_ctx.get_in_nodes()[:2]]

        if input_a.is_const(check_quant=True):
            errors.append(OpInputErrorInfo(input_index=0, input_name=input_a_name, reason=cls.error_first_input))
        if not input_b.is_const(check_quant=True):
            errors.append(OpInputErrorInfo(input_index=1, input_name=input_b_name, reason=cls.error_second_input))
        # onnx allows 2nd input of rank 2 only
        assert len(graph_ctx.get_in_shapes()[1]) == 2
        get_attr = onnx_node.get_attr_with_default_from_schema
        alpha = get_attr('alpha')
        beta = get_attr('beta')
        transpose_a = get_attr('transA')
        transpose_b = get_attr('transB')

        if not np.isclose(alpha, cls.supported_factor):
            errors.append(ParamErrorInfo(name='alpha', value=alpha, reason=cls.error_invalid_factor))
        if not np.isclose(beta, cls.supported_factor):
            errors.append(ParamErrorInfo(name='beta', value=beta, reason=cls.error_invalid_factor))
        if transpose_a not in cls.supported_transpose_a:
            errors.append(ParamErrorInfo(name='transA', value=transpose_a, reason=cls.error_invalid_transpose_a))

        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='Gemm -> FullyConnected')

        node = FullyConnected(onnx_node.name, history=history)

        has_bias = len(graph_ctx.get_in_shapes()) == 3
        weight_shape = graph_ctx.get_in_shapes()[1]
        out_channels = weight_shape[0 if transpose_b else 1]

        if has_bias:
            request = None
        else:
            b_idx = node.InputsIndex.BIAS.value
            bias_const = cls.get_bias_const(graph_ctx, has_bias, node, out_channels)
            cfg = {b_idx: bias_const}
            request = GraphRequest(const_inputs_to_insert=cfg)
        if transpose_b:
            node.weight_semantics = TensorSemantics(AxisSemantics.OUT_CHANNELS, AxisSemantics.IN_CHANNELS)
        else:
            node.weight_semantics = TensorSemantics(AxisSemantics.IN_CHANNELS, AxisSemantics.OUT_CHANNELS)
        return node, request

    @classmethod
    def get_bias_const(cls, graph_ctx, has_bias, node, out_channels):
        if has_bias:
            bias_node = graph_ctx.get_in_nodes()[2]
            bias_const = ConstNodeCfg(bias_node.name + "_new", bias_node.get_const_data())
        else:
            bias_const = ConstNodeCfg(node.name + '_bias', node.zero_bias(out_channels))
        return bias_const
