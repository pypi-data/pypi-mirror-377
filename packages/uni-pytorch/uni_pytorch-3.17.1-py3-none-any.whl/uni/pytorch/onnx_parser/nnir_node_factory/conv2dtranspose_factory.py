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
Created on 5/10/23

@author: irenab
"""
from typing import Tuple, Optional
from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Conv2dTransposeBias
from uni.common.core.nnir_graph.nnir_nodes.common import Param2d
from uni.common.core.nnir_graph.semantics import TensorSemantics, AxisSemantics
from uni.common.core.error import raise_op_param_error
from uni.common.core.node_history import NodeHistory
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from ._op2d_mixin import OnnxOp2dMixin
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx


class Conv2dTransposeOnnxFactory(OnnxFactoryBase, OnnxOp2dMixin):
    onnx_weight_semantics = TensorSemantics(AxisSemantics.IN_CHANNELS,
                                            AxisSemantics.OUT_CHANNELS,
                                            AxisSemantics.KERNEL_H,
                                            AxisSemantics.KERNEL_W)  # yapf: disable

    implicit_pad_error = 'Inferring pads from output_shape is not supported.'

    @classmethod
    @validate_onnx(num_inputs=[2, 3],
                   num_outputs=1,
                   attrs=[],
                   optional_attrs=['kernel_shape', 'strides', 'dilations', 'pads', 'group', 'auto_pad'] +
                   ['output_padding', 'output_shape'])
    def from_onnx(cls, onnx_node: OnnxMetaNode,
                  graph_ctx: NodeGraphContext) -> Tuple[Conv2dTransposeBias, Optional[GraphRequest]]:
        """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#ConvTranspose """
        # Onnx Conv op supports any #dims NxCxD1...Di
        # if this validation fails, further validation is pointless, so raising immediately
        cls.validate_2d_op_data_shape(onnx_node, graph_ctx)

        group = onnx_node.get_attr_with_default_from_schema('group')

        dilation = Param2d(*onnx_node.get_attr_with_default('dilations', (1, 1)))
        stride = Param2d(*onnx_node.get_attr_with_default('strides', (1, 1)))

        kernel_size = None
        if onnx_node.has_attr('kernel_shape'):
            kernel_size = Param2d(*onnx_node.get_attr('kernel_shape'))

        out_shape = onnx_node.get_attr_with_default('output_shape', None)
        if out_shape is not None:
            # if explicit output shape is passed pads is ignored and recalculated based on output_shape + output_padding
            raise_op_param_error(cls.onnx_op_info(onnx_node), 'output_shape', out_shape, cls.implicit_pad_error, None)

        input_shapes = graph_ctx.get_in_shapes()
        # if kernel_size is None, it will be extracted from weights dims
        has_bias, (w_out_channels, w_in_channels), kernel_size = Conv2dTransposeBias.validate_and_query_weights(
            input_shapes, cls.onnx_weight_semantics, kernel_size=kernel_size)
        assert kernel_size is not None

        pad2d, _ = cls.read_and_validate_pad(onnx_node)
        assert pad2d
        out_pad = Param2d(*onnx_node.get_attr_with_default('output_padding', (0, 0)))
        node = Conv2dTransposeBias(onnx_node.name,
                                   kernel_size=kernel_size,
                                   stride=stride,
                                   dilation=dilation,
                                   groups=group,
                                   pad=pad2d,
                                   out_pad=out_pad,
                                   history=NodeHistory(cls.onnx_op_info(onnx_node), desc=''))
        node.weight_semantics = cls.onnx_weight_semantics
        node.data_format = cls.data_format

        out_channels = w_out_channels * group
        request = None if has_bias else node.request_add_zero_bias(node.name, out_channels)
        return node, request
