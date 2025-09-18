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
from typing import Sequence, Tuple

from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.nnir_graph.nnir_nodes import ReluX
from uni.common.core.node_history import NodeHistory
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeGraphContext
from uni.common.core.error.util import supported_vals_msg, raise_op_error
from uni.common.core.error.defs import ParamErrorInfo


class OnnxClipToNnirNode(OnnxFactoryBase):
    supported_low_vals = [0]
    invalid_low_error_msg = supported_vals_msg(supported_low_vals)

    @classmethod
    @validate_onnx(num_inputs=[1, 2, 3], num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> Tuple[ReluX, GraphRequest]:
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        # low/high are optional. Inputs can either be missing altogether in node inputs list, or be empty,
        # In the latter case DummyInput node is added
        from uni.pytorch.onnx_parser.onnx_parser import is_dummy_input
        low, high = None, None
        if len(in_nodes) > 1 and not is_dummy_input(in_nodes[1]):
            low = in_nodes[1].get_const_data()
        if len(in_nodes) > 2 and not is_dummy_input(in_nodes[2]):
            high = in_nodes[2].get_const_data()

        errs = []
        if low not in cls.supported_low_vals:
            errs.append(ParamErrorInfo('low', low, cls.invalid_low_error_msg))
        if errs:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errs, history=None)

        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='Clip -> ReluX')
        req = GraphRequest(inputs_to_detach=list(range(len(in_nodes)))[1:])
        return ReluX(onnx_node.name, x=high, history=history), req
