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
Created on 3/20/23

@author: irenab
"""
from typing import Tuple, Optional, List    # noqa: F401
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.nnir_graph.nnir_nodes import Split
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeGraphContext

opset_13_optional_attrs = ['axis']
opset_18_optional_attrs = ['num_outputs']


class OnnxSplitNnirNode(OnnxFactoryBase):
    """
    https://github.com/onnx/onnx/blob/main/docs/Changelog.md#Split-13
    https://github.com/onnx/onnx/blob/main/docs/Changelog.md#Split-18
    opset 18:
        new attribute 'num_outputs'
    """

    @classmethod
    @validate_onnx(num_inputs=[1, 2],
                   num_outputs=None,
                   attrs=[],
                   optional_attrs=opset_13_optional_attrs + opset_18_optional_attrs,
                   opset_limits=(13, 20))
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> Tuple[Split, Optional[GraphRequest]]:
        axis = onnx_node.get_attr_with_default_from_schema('axis')
        in_nodes = graph_ctx.get_in_nodes()    # type: List
        request = None
        splits = graph_ctx.get_out_degree()
        if len(in_nodes) > 1:
            request = GraphRequest(inputs_to_detach=[1])
            if not onnx_node.is_dummy_input():
                splits = in_nodes[1].get_const_data().tolist()

        node = Split(onnx_node.name, axis=axis, num_splits_or_sizes=splits)
        return node, request
