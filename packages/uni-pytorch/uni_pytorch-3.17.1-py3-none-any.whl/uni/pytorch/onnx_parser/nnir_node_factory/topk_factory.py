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
from typing import Sequence, Tuple

from uni.common.core.error import ParamErrorInfo, supported_vals_msg, raise_op_error

from uni.common.core.multigraph.node_graph_api import GraphRequest

from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.nnir_graph.nnir_nodes import TopK
from uni.common.core.node_history import NodeHistory
from uni.pytorch.onnx_parser import OnnxMetaNode


class OnnxTopKToNnirNode(OnnxFactoryBase):
    """ https://github.com/onnx/onnx/blob/main/docs/Changelog.md#TopK """

    supported_largest_vals = [1]
    invalid_largest_error_msg = supported_vals_msg(supported_largest_vals)
    only_last_axis_error = "Only last axis is supported"

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=2, attrs=[], optional_attrs=["axis", "largest", "sorted"])
    def from_onnx(cls, onnx_node, graph_ctx=None) -> Tuple[TopK, GraphRequest]:
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        k = list(in_nodes[1].get_const_data())[0]
        axis = onnx_node.get_attr_with_default_from_schema("axis")
        largest = onnx_node.get_attr_with_default_from_schema("largest")

        errors = []
        in_shape = graph_ctx.get_in_shapes()[0]
        last_axis = len(in_shape) - 1

        if axis not in [-1, last_axis]:
            errors.append(ParamErrorInfo(name="axis", value=axis, reason=cls.only_last_axis_error))
        if largest not in cls.supported_largest_vals:
            errors.append(ParamErrorInfo(name="largest", value=largest, reason=cls.invalid_largest_error_msg))
        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

        is_sorted = onnx_node.get_attr_with_default_from_schema("sorted")
        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='')
        req = GraphRequest(inputs_to_detach=list(range(len(in_nodes)))[1:])
        return TopK(name=onnx_node.name, k=int(k), is_sorted=bool(is_sorted), history=history), req
