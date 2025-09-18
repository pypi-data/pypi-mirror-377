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
from typing import List, Union, Tuple

import numpy as np

from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from ._op2d_mixin import OnnxOp2dMixin
from uni.common.core.error import ParamErrorInfo, ErrorInfo
from uni.common.core.error.util import raise_op_error, supported_vals_msg
from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest, NodeToInsertCfg, NodePosition
from uni.common.core.nnir_graph.nnir_nodes import AveragePool2d, Pad
from uni.common.core.nnir_graph.nnir_nodes.common import Param2d, Padding2d
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode

opset_11_optional_attrs = ["auto_pad", "ceil_mode", "count_include_pad", "pads", "strides"]
opset_19_required_attrs = ["dilations"]


class OnnxAveragePoolToNnirNode(OnnxFactoryBase, OnnxOp2dMixin):
    ceil_mode_value = 0

    error_ceil_mode = supported_vals_msg([ceil_mode_value])
    error_msg_dilations = "Only lists of 1's are supported."

    @classmethod
    @validate_onnx(num_inputs=1,
                   num_outputs=1,
                   attrs=["kernel_shape"],
                   optional_attrs=opset_11_optional_attrs + opset_19_required_attrs,
                   opset_limits=(11, 21))
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) \
            -> Union[AveragePool2d, Tuple[AveragePool2d, GraphRequest]]:
        """
            https://github.com/onnx/onnx/blob/main/docs/Changelog.md#AveragePool-11
            https://github.com/onnx/onnx/blob/main/docs/Changelog.md#AveragePool-19

            from torch 2.1 count_include_pad is 1 by default
            so in this case we change add pad before average pool

            opset 19:
                new attribute dilations

        """
        # Onnx op supports any #dims NxCxD1...Di
        cls.validate_2d_op_data_shape(onnx_node, graph_ctx)
        errors: List[ErrorInfo] = []

        # read auto_pad and pads attributes
        # Errors found in pad will be raised immediately, as pad2d is a dependency for the ceil calculation
        pad2d, pad_errs = cls.read_and_validate_pad(onnx_node)
        assert pad2d

        kernel_size = Param2d(*onnx_node.get_attr('kernel_shape'))
        stride = Param2d(*onnx_node.get_attr_with_default('strides', (1, 1)))
        ceil_mode = onnx_node.get_attr_with_default_from_schema("ceil_mode")
        count_include_pad = onnx_node.get_attr_with_default_from_schema("count_include_pad")
        dilations = onnx_node.get_attr_with_default('dilations', None)

        if dilations is not None and set(dilations) != {1}:
            errors.append(ParamErrorInfo(name='dilations', value=dilations, reason=cls.error_msg_dilations))

        if ceil_mode != cls.ceil_mode_value:
            if ceil_mode == 1 and not cls.is_ceil_mode_have_meaning(graph_ctx, kernel_size, pad2d, stride):
                pass
            else:
                errors.append(ParamErrorInfo(name='ceil_mode', value=ceil_mode, reason=cls.error_ceil_mode))

        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

        if count_include_pad == 0 or pad2d.is_empty():
            node = AveragePool2d(onnx_node.name,
                                 kernel_size=Param2d(*kernel_size),
                                 stride=Param2d(*stride),
                                 padding=pad2d)
            node.data_format = cls.data_format
            return node

        padding = np.zeros((4, 2), dtype=np.int32)
        padding[2][0], padding[2][1] = pad2d.h
        padding[3][0], padding[3][1] = pad2d.w
        pad_node = Pad("pad_before_" + onnx_node.name, paddings=padding, pad_const=0.)
        avg_node = AveragePool2d(onnx_node.name,
                                 kernel_size=Param2d(*kernel_size),
                                 stride=Param2d(*stride),
                                 padding=Padding2d())
        avg_node.data_format = cls.data_format
        pad_out_shape = list(graph_ctx.get_in_shapes()[0])
        pad_out_shape[2] += pad2d.h[0] + pad2d.h[1]
        pad_out_shape[3] += pad2d.w[0] + pad2d.w[1]
        subsequent_node_to_insert = NodeToInsertCfg(pad_node,
                                                    tuple(pad_out_shape),
                                                    node_position=NodePosition.NODE_BEFORE)
        request = GraphRequest(adjacent_node_to_insert=subsequent_node_to_insert)
        return avg_node, request

    @classmethod
    def is_ceil_mode_have_meaning(cls, graph_ctx, kernel, pad2d, strides):
        if strides == (1, 1):
            return False

        in_shape = graph_ctx.get_in_shapes()[0]
        s_h, s_w = strides
        numerator_h = in_shape[2] + pad2d.h[0] + pad2d.h[1] - kernel[0]
        numerator_w = in_shape[3] + pad2d.w[0] + pad2d.w[1] - kernel[1]
        return numerator_h % s_h != 0 or numerator_w % s_w != 0
