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
from typing import Tuple, Optional

from uni.common.core.error import supported_vals_msg
from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Conv2dBias
from uni.common.core.nnir_graph.nnir_nodes.common import Param2d
from uni.common.core.nnir_graph.semantics import TensorSemantics, AxisSemantics
from uni.common.core.node_history import NodeHistory
from uni.common.parsers._pad_util import ExcessPaddingLocation, calc_same_padding
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from ._op2d_mixin import OnnxOp2dMixin
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx


class Conv2dOnnxFactory(OnnxFactoryBase, OnnxOp2dMixin):
    onnx_weight_semantics = TensorSemantics(AxisSemantics.OUT_CHANNELS,
                                            AxisSemantics.IN_CHANNELS,
                                            AxisSemantics.KERNEL_H,
                                            AxisSemantics.KERNEL_W)  # yapf: disable

    same_autopads = ['SAME_UPPER', 'SAME_LOWER']
    supported_autopad = ['NOTSET', 'VALID'] + same_autopads
    error_unsupported_pad = supported_vals_msg(supported_autopad)

    @classmethod
    @validate_onnx(num_inputs=[2, 3],
                   num_outputs=1,
                   attrs=[],
                   optional_attrs=['kernel_shape', 'strides', 'dilations', 'pads', 'group', 'auto_pad'])
    def from_onnx(cls, onnx_node: OnnxMetaNode,
                  graph_ctx: NodeGraphContext) -> Tuple[Conv2dBias, Optional[GraphRequest]]:
        """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#Conv """
        # Onnx Conv op supports any #dims NxCxD1...Di
        # if this validation fails, further validation is pointless, so raising immediately
        cls.validate_2d_op_data_shape(onnx_node, graph_ctx)

        group = onnx_node.get_attr_with_default_from_schema('group')

        dilation = Param2d(*onnx_node.get_attr_with_default('dilations', (1, 1)))
        stride = Param2d(*onnx_node.get_attr_with_default('strides', (1, 1)))

        kernel_size = None
        if onnx_node.has_attr('kernel_shape'):
            kernel_size = Param2d(*onnx_node.get_attr('kernel_shape'))

        input_shapes = graph_ctx.get_in_shapes()
        # If kernel_size is None, it will be extracted from weights dims
        # Weights for all groups are stacked together, so w_in_channels correspond to a single group but
        # w_out_channels correspond to layer out_channels = out_group_size*groups
        has_bias, (out_channels,
                   w_in_channels), kernel_size = Conv2dBias.validate_and_query_weights(input_shapes,
                                                                                       cls.onnx_weight_semantics,
                                                                                       kernel_size=kernel_size)
        assert kernel_size is not None

        out_group_size = out_channels // group

        auto_pad = onnx_node.get_attr_with_default_from_schema('auto_pad')
        pad2d, _ = cls.read_and_validate_pad(onnx_node)

        if auto_pad in cls.same_autopads:
            excess_padding_location = ExcessPaddingLocation.UPPER if auto_pad == 'SAME_UPPER' else\
                                                                                            ExcessPaddingLocation.LOWER
            h_axis, w_axis = cls.data_format.get_hw_axes()
            input_h = input_shapes[0][h_axis]
            input_w = input_shapes[0][w_axis]
            pad2d = calc_same_padding(input_h, input_w, kernel_size, stride, dilation, excess_padding_location)

        assert pad2d
        node = Conv2dBias(onnx_node.name,
                          kernel_size=kernel_size,
                          stride=stride,
                          dilation=dilation,
                          group=group,
                          pad2d=pad2d,
                          input_group_size=w_in_channels,
                          out_group_size=out_group_size,
                          data_format=cls.data_format,
                          weight_semantics=cls.onnx_weight_semantics,
                          history=NodeHistory(cls.onnx_op_info(onnx_node), desc=''))
        node.weight_semantics = cls.onnx_weight_semantics
        node.data_format = cls.data_format

        request = None if has_bias else node.request_add_zero_bias(node.name, out_channels)
        return node, request
