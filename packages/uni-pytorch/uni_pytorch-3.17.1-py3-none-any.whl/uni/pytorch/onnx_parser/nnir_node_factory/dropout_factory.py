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
Created on 2/8/23

@author: irenab
"""
from typing import Tuple

from uni.common.core.nnir_graph.nnir_nodes import Identity
from uni.common.core.node_history import NodeHistory
from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest
from uni.common.core.error.util import raise_op_input_error, raise_op_output_error, training_mode_error
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx


class OnnxDropoutToNnirNode(OnnxFactoryBase):
    """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#Dropout """

    output_mask_error = 'Output mask tensor connected to another node is not supported'

    @classmethod
    @validate_onnx(num_inputs=[1, 2, 3], num_outputs=[1, 2], attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> Tuple[Identity, GraphRequest]:
        deg_in = graph_ctx.get_in_degree()
        if deg_in > 2:
            train: OnnxMetaNode = graph_ctx.get_in_nodes()[2]
            # numpy bool will always return False in "if x is True" expression. So the cast is only for future safety
            if not train.is_dummy_input() and bool(train.get_const_data()):
                raise_op_input_error(cls.onnx_op_info(onnx_node), 2, train.name, training_mode_error, None)

        if graph_ctx.get_out_degree() > 1:
            raise_op_output_error(cls.onnx_op_info(onnx_node), 1, 'mask tensor', cls.output_mask_error, None)

        history = NodeHistory(cls.onnx_op_info(onnx_node), desc=f'{onnx_node.op_type} -> Identity')
        node = Identity(onnx_node.name, history=history)
        request = GraphRequest(inputs_to_detach=list(range(1, deg_in)))
        return node, request
