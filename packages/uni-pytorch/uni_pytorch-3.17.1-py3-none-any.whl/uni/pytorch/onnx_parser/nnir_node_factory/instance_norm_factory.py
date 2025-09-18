# -------------------------------------------------------------------------------
# (c) Copyright 2025 Sony Semiconductor Israel, Ltd. All rights reserved.
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

from uni.common.core.multigraph.node_graph_api import NodeGraphContext

from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.nnir_graph.nnir_nodes import InstanceNorm


class OnnxInstanceNormToNnirNode(OnnxFactoryBase):
    """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#InstanceNormalization """

    @classmethod
    @validate_onnx(num_inputs=[3], num_outputs=[1], attrs=[], optional_attrs=['epsilon'])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> InstanceNorm:
        epsilon = onnx_node.get_attr_with_default_from_schema('epsilon')
        num_groups = graph_ctx.get_in_shapes()[1][0]
        return InstanceNorm(onnx_node.name, num_groups=num_groups, epsilon=epsilon)
