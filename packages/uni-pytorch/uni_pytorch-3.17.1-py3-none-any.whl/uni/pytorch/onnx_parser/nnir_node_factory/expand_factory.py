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
from typing import Sequence, Tuple

from uni.common.core.error import ParamErrorInfo, raise_op_error
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Broadcast
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx


class OnnxExpandToNnirNode(OnnxFactoryBase):
    """
        https://github.com/onnx/onnx/blob/main/docs/Operators.md#Expand

        Handles complex case of expend on dyadic batch that updated by onnx simplifier to invalid broadcast
        see on test test_torch_dynamic_batch in test_expand_torch.py

    """

    const_input_index = 1

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx=None) -> Tuple[Broadcast, GraphRequest]:
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        assert len(in_nodes) == 2
        const_input = in_nodes[cls.const_input_index]
        target_shape = tuple(const_input.get_const_data())
        input_shape = graph_ctx.get_in_shapes()[0]
        broadcast_shape = None
        try:
            broadcast_shape = cls.calculate_broadcast_shape(input_shape, target_shape)
        except ValueError as e:
            error = ParamErrorInfo(name='shape', value=target_shape, reason=str(e))
            raise_op_error(cls.onnx_op_info(onnx_node), [error], None)
        assert broadcast_shape is not None
        return Broadcast(onnx_node.name, shape=broadcast_shape), GraphRequest(inputs_to_detach=[cls.const_input_index])

    @staticmethod
    def calculate_broadcast_shape(in_shape, target_shape):
        """
        Calculate the broadcast shape between the input tensor shape and the target shape.
        Args:
            in_shape: input tensor shape values > 0
            target_shape: target shape to broadcast to values > 0 or -1 for broadcast
        Returns:
            broadcast_shape: the broadcast shape
        """
        org_in_shape = [i for i in in_shape]
        org_target_shape = [i for i in target_shape]

        in_shape = [i if i is not None else 1 for i in in_shape]
        target_shape = [i if i is not None else 1 for i in target_shape]
        in_shape = in_shape[::-1]
        target_shape = target_shape[::-1]
        broadcast_shape = []
        for i in range(max(len(in_shape), len(target_shape))):
            in_dim = in_shape[i] if i < len(in_shape) else 1
            t_dim = target_shape[i] if i < len(target_shape) else 1

            if t_dim == -1:
                broadcast_shape.append(in_dim)
            elif in_dim == 1 or t_dim == 1:
                broadcast_shape.append(max(in_dim, t_dim))
            elif in_dim == t_dim:
                broadcast_shape.append(in_dim)
            else:
                raise ValueError(f"Cannot broadcast shape {org_in_shape} to {org_target_shape}")
        return tuple(broadcast_shape[::-1])
