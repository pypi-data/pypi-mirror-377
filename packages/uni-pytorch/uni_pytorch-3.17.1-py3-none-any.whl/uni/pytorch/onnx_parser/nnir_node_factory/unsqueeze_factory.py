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

from typing import Tuple, Sequence

from uni.common.core.error import raise_op_param_error
from uni.common.core.nnir_graph.nnir_nodes.expand_dims import ExpandDims
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.node_history import NodeHistory
from uni.common.core.multigraph.node_graph_api import GraphRequest


class OnnxUnSqueezeToNnirNode(OnnxFactoryBase):
    only_one_axis_msg = 'Only one axis is supported'

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx=None) -> Tuple[ExpandDims, GraphRequest]:
        """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#Unsqueeze """

        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        axes = in_nodes[1].get_const_data()
        if axes.size > 1:
            raise_op_param_error(cls.onnx_op_info(onnx_node),
                                 param_name='axes',
                                 param_value=axes.tolist(),
                                 reason=cls.only_one_axis_msg,
                                 history=None)

        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='')
        req = GraphRequest(inputs_to_detach=[1])
        return ExpandDims(onnx_node.name, axis=int(axes.item()), history=history), req
