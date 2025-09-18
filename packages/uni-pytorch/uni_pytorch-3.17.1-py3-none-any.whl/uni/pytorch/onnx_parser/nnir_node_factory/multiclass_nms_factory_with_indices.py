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
from typing import Tuple

from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.nnir_graph.nnir_nodes import ExpandDims, MultiClassNonMaxSuppression
from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeToInsertCfg, NodePosition
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx


class OnnxMultiClassNMSWithIndicesToNnirNode(OnnxFactoryBase):

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=5, attrs=['score_threshold', 'iou_threshold', 'max_detections'])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx=None) \
            -> Tuple[MultiClassNonMaxSuppression, GraphRequest]:
        nms = MultiClassNonMaxSuppression(onnx_node.name,
                                          score_threshold=onnx_node.attr['score_threshold'],
                                          iou_threshold=onnx_node.attr['iou_threshold'],
                                          max_detections=onnx_node.attr['max_detections'])
        expand_dims = ExpandDims(onnx_node.name + '_expand_dims', axis=2)
        boxes_shape = graph_ctx.get_in_shapes()[MultiClassNonMaxSuppression.Inputs.Boxes]
        expanded_shape = (*boxes_shape[:2], 1, boxes_shape[2])
        request = GraphRequest(adjacent_node_to_insert=NodeToInsertCfg(
            expand_dims, expanded_shape, NodePosition.NODE_BEFORE, edge_index=MultiClassNonMaxSuppression.Inputs.Boxes))
        return nms, request
