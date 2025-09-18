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
from typing import Tuple, Sequence

from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest, ConstNodeCfg
from uni.common.core.nnir_graph.nnir_nodes import FasterRCNNBoxDecode
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory import OnnxFactoryBase, validate_onnx


class OnnxBoxDecodeToNnirNode(OnnxFactoryBase):

    @classmethod
    @validate_onnx(num_inputs=[4], num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) \
            -> Tuple[FasterRCNNBoxDecode, GraphRequest]:
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        anchors = in_nodes[1].get_const_data()
        scale_factors = tuple(map(float, in_nodes[2].get_const_data()))
        clip_window = tuple(map(float, in_nodes[3].get_const_data()))
        nnir_node = FasterRCNNBoxDecode(onnx_node.name, scale_factors=scale_factors, clip_window=clip_window)
        const_cfg = ConstNodeCfg(onnx_node.name + '/anchors', data=anchors)
        request = GraphRequest(const_inputs_to_insert={FasterRCNNBoxDecode.Inputs.Anchors: const_cfg},
                               inputs_to_detach=[1, 2, 3])
        return nnir_node, request
