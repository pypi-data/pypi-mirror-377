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

from typing import Sequence

import onnx

from uni.common.core.error import ParamErrorInfo, raise_op_error
from uni.common.core.multigraph.edge import Edge
from uni.common.logger import get_logger, MessageCodes
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.nnir_graph.nnir_nodes import Identity
from uni.common.core.node_history import NodeHistory
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.multigraph.node_graph_api import NodeGraphContext

logger = get_logger(__name__)


class OnnxCastToNnirNode(OnnxFactoryBase):

    @staticmethod
    def get_error_msg(from_np_dtype, to_np_dtype):
        return f'Cast from {from_np_dtype} to {to_np_dtype} is not supported'

    @classmethod
    @validate_onnx(num_inputs=1, num_outputs=1, attrs=['to'])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> Identity:
        in_edges: Sequence[Edge] = graph_ctx.get_in_edges()
        assert len(in_edges) == 1, f'Cast node {onnx_node.name} has more than one input edge'

        to_dtype = onnx_node.get_attr('to')
        to_np_dtype = onnx.mapping.TENSOR_TYPE_MAP[to_dtype].np_dtype
        from_np_dtype = in_edges[0].np_dtype
        if from_np_dtype is None:
            logger.warning(f'Cast node {onnx_node.name} has unknown input dtype', message_code=MessageCodes.EXECUTION)

        if from_np_dtype is not None and to_np_dtype != from_np_dtype:
            error = ParamErrorInfo(name='to', value=to_np_dtype, reason=cls.get_error_msg(from_np_dtype, to_np_dtype))
            raise_op_error(cls.onnx_op_info(onnx_node), errors=[error], history=None)

        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='Cast -> Identity')
        return Identity(onnx_node.name, history=history)
