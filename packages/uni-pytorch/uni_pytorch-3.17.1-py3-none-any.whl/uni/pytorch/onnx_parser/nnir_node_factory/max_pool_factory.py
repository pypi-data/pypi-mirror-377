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
from typing import List

from uni.common.core.error import ParamErrorInfo, OpOutputErrorInfo, ErrorInfo
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from ._op2d_mixin import OnnxOp2dMixin
from uni.common.core.error.util import raise_op_error, supported_vals_msg
from uni.common.core.multigraph.node_graph_api import NodeGraphContext
from uni.common.core.nnir_graph.nnir_nodes import MaxPool2d
from uni.common.core.nnir_graph.nnir_nodes.common import Param2d
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode


class OnnxMaxPoolToNnirNode(OnnxFactoryBase, OnnxOp2dMixin):

    ceil_mode_value = 0
    storage_order_value = 0
    dilations_value = (1, 1)

    error_dilations = supported_vals_msg([dilations_value])
    error_ceil_mode = supported_vals_msg([ceil_mode_value])
    error_storage_order = supported_vals_msg([storage_order_value])
    error_indices = "Indices output is not supported for MaxPool2d"

    @classmethod
    @validate_onnx(num_inputs=1,
                   num_outputs=[1, 2],
                   attrs=["kernel_shape"],
                   optional_attrs=["auto_pad", "ceil_mode", "dilations", "pads", "storage_order", "strides"])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> MaxPool2d:
        """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#MaxPool """
        # Onnx op supports any #dims NxCxD1...Di
        cls.validate_2d_op_data_shape(onnx_node, graph_ctx)
        errors: List[ErrorInfo] = []

        # read auto_pad and pads attributes
        pad2d, pad_errs = cls.read_and_validate_pad(onnx_node, return_error=True)
        if pad_errs:
            errors.extend(pad_errs)

        ceil_mode = onnx_node.get_attr_with_default_from_schema("ceil_mode")
        if ceil_mode != cls.ceil_mode_value:
            errors.append(ParamErrorInfo(name='ceil_mode', value=ceil_mode, reason=cls.error_ceil_mode))

        dilations = tuple(onnx_node.get_attr_with_default("dilations", cls.dilations_value))
        if dilations != cls.dilations_value:
            errors.append(ParamErrorInfo(name='dilations', value=dilations, reason=cls.error_dilations))

        kernel_size = Param2d(*onnx_node.get_attr('kernel_shape'))
        stride = Param2d(*onnx_node.get_attr_with_default('strides', (1, 1)))

        if len(graph_ctx.get_out_shapes()) == 2:
            errors.append(OpOutputErrorInfo(output_index=1, output_name='Indices tensor', reason=cls.error_indices))
        storage_order = onnx_node.get_attr_with_default_from_schema("storage_order")
        if storage_order != cls.storage_order_value:
            errors.append(ParamErrorInfo(name='storage_order', value=storage_order, reason=cls.error_storage_order))

        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

        assert pad2d
        node = MaxPool2d(onnx_node.name, kernel_size=Param2d(*kernel_size), stride=Param2d(*stride), padding=pad2d)
        node.data_format = cls.data_format
        return node
