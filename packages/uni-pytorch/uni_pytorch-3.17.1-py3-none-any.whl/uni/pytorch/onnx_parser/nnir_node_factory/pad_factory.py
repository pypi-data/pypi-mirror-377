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
from typing import Tuple, Sequence, List

import numpy as np

from uni.common.core.error import supported_vals_msg, ParamErrorInfo, raise_op_error, OpInputErrorInfo, ErrorInfo
from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Pad
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx

expected_num_inputs = [2, 3, 4]


class OnnxPadToNnirNode(OnnxFactoryBase):
    constant_mode = "constant"
    supported_mode = [constant_mode]
    invalid_mode_error = supported_vals_msg(supported_mode)
    invalid_negative_pads_error = "negative pads are not supported"
    invalid_axes_error = ("Axes must be a list of integers in the range [0, rank-1]. "
                          "Negative values are allowed, but the axes must be in order.")

    @classmethod
    @validate_onnx(num_inputs=expected_num_inputs,
                   num_outputs=1,
                   attrs=[],
                   optional_attrs=["mode"],
                   opset_limits=(13, 20))
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> Tuple[Pad, GraphRequest]:
        """
        https://github.com/onnx/onnx/blob/main/docs/Changelog.md#Pad-13
        https://github.com/onnx/onnx/blob/main/docs/Changelog.md#Pad-18
        https://github.com/onnx/onnx/blob/main/docs/Changelog.md#Pad-19
        opset 18:
            new optional input axes - not supported
        opset 19:
            mode attribute - add 'warp' mode - only 'constant' is supported
        """
        mode = onnx_node.get_attr_with_default_from_schema("mode")
        errors: List[ErrorInfo] = []
        if mode not in cls.supported_mode:
            errors.append(ParamErrorInfo(name="mode", value=mode, reason=cls.invalid_mode_error))

        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        padding = in_nodes[1].get_const_data()
        if padding.min() < 0:
            errors.append(ParamErrorInfo(name="pads", value=padding, reason=cls.invalid_negative_pads_error))

        if len(in_nodes) == 3 and not in_nodes[2].is_dummy_input():
            constant_value = in_nodes[2].get_const_data().item()
        else:
            constant_value = 0.

        if len(in_nodes) == 4 and not in_nodes[3].is_dummy_input():
            axes = in_nodes[3].get_const_data()
            in_rank = len(graph_ctx.get_in_shapes()[0])
            if not cls.validate_full_axes(axes, in_rank):
                errors.append(OpInputErrorInfo(input_index=3, input_name="axes", reason=cls.invalid_axes_error))

        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

        rank = len(padding) // 2
        padding = np.array([[padding[i], padding[i + rank]] for i in range(rank)], dtype=np.int64)

        inputs_to_detach = list(range(1, len(in_nodes)))

        node = Pad(onnx_node.name, paddings=padding, pad_const=constant_value)
        return node, GraphRequest(inputs_to_detach=inputs_to_detach)

    @staticmethod
    def validate_full_axes(axes, in_rank):
        if axes is None:
            return True
        if len(axes) != in_rank:
            return False
        axes = [a if a >= 0 else a + in_rank for a in axes]
        return list(axes) == list(range(in_rank))
