# -------------------------------------------------------------------------------
# (c) Copyright 2024 Sony Semiconductor Israel, Ltd. All rights reserved.
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
Created on 10/6/24

@author: lotanw
"""
from typing import Union, Tuple

from uni.common.core.error import raise_op_error, OpInputErrorInfo, supported_vals_msg
from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Sqrt, Identity, Mul
from uni.common.core.node_history import NodeHistory
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory import OnnxFactoryBase, validate_onnx


class OnnxPowToNnirNode(OnnxFactoryBase):
    """
        expects x base and y exponent
        supports y == 0.5, which will be converted to Sqrt node.
        supports y == 1, which will be converted to Identity node.
        supports y == 2, which will be converted to Mul node.
    """

    supported_exp_values = [0.5, 1, 2]
    unsupported_exp_err_msg = supported_vals_msg(supported_exp_values)
    sqrt_history_msg = 'Pow with exp == 0.5 -> Sqrt'
    identity_history_msg = 'Pow with exp == 1 -> Identity'
    power_of_2_history_msg = 'Pow with exp == 2 -> Mul'

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=1, attrs=[], optional_attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode,
                  graph_ctx: NodeGraphContext) -> Tuple[Union[Sqrt, Identity, Mul], GraphRequest]:
        """  https://github.com/onnx/onnx/blob/main/docs/Operators.md#Pow """
        errors = []
        in_nodes = graph_ctx.get_in_nodes()
        exp_value = float(in_nodes[1].attr["value"])
        if exp_value not in cls.supported_exp_values:
            errors.append(OpInputErrorInfo(1, "exponent", cls.unsupported_exp_err_msg))
        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

        req = GraphRequest(inputs_to_detach=[1])
        if exp_value == 0.5:
            history = NodeHistory(cls.onnx_op_info(onnx_node), desc=cls.sqrt_history_msg)
            return Sqrt(f'{onnx_node.name}', history=history), req
        if exp_value == 1:
            history = NodeHistory(cls.onnx_op_info(onnx_node), desc=cls.identity_history_msg)
            return Identity(f'{onnx_node.name}', history=history), req
        if exp_value == 2:
            dynamic_input_to_duplicate = {0: [1]}
            dup_req = GraphRequest(inputs_to_detach=[1], dynamic_input_to_duplicate=dynamic_input_to_duplicate)
            history = NodeHistory(cls.onnx_op_info(onnx_node), desc=cls.power_of_2_history_msg)
            return Mul(f'{onnx_node.name}', history=history), dup_req
        raise NotImplementedError(f"unsupported exp value {exp_value}")
