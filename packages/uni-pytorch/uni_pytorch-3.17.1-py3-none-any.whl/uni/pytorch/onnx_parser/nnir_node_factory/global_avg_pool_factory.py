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
from ._op2d_mixin import OnnxOp2dMixin
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.multigraph.node_graph_api import NodeGraphContext
from uni.common.core.nnir_graph.semantics import SemanticsHelper, DataFormat
from uni.common.core.nnir_graph.nnir_nodes import AveragePool2d
from uni.common.core.nnir_graph.nnir_nodes.common import Param2d, Padding2d
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode


class OnnxGlobalAvgPoolToNnirNode(OnnxFactoryBase, OnnxOp2dMixin):

    @classmethod
    @validate_onnx(num_inputs=1, num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> AveragePool2d:
        """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#GlobalAveragePool """

        input_shape = graph_ctx.get_in_shapes()[0]
        # Onnx op supports any #dims NxCxD1...Di
        cls.validate_2d_op_data_shape(onnx_node, graph_ctx)

        # get h and w sizes
        helper = SemanticsHelper(DataFormat.CHW)
        h = input_shape[helper.data_h_axis()]
        w = input_shape[helper.data_w_axis()]
        node = AveragePool2d(onnx_node.name, kernel_size=Param2d(h, w), stride=Param2d(1, 1), padding=Padding2d())
        node.data_format = cls.data_format
        return node
