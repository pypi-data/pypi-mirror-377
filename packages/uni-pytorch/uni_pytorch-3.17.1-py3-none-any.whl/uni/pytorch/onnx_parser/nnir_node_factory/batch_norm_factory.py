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
from typing import Tuple

from uni.common.core.multigraph.node_graph_api import ConstNodeCfg, GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import BatchNorm
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx

TORCH_CHANNELS_AXIS = 1


class OnnxBatchNormToNnirNode(OnnxFactoryBase):
    """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#BatchNormalization"""

    @classmethod
    @validate_onnx(num_inputs=[5], num_outputs=1, attrs=[], optional_attrs=["epsilon", "momentum", "training_mode"])
    def from_onnx(cls, node: OnnxMetaNode, graph_ctx=None) -> Tuple[BatchNorm, GraphRequest]:

        gamma, beta, mean, variance = [c.get_const_data() for c in graph_ctx.get_in_nodes()[1:]]
        epsilon = node.get_attr_with_default_from_schema("epsilon")

        # torch BatchNorm2d only supports axis=1 and 4d input. ONNX supports any num_dims
        # here we convert the gamma, beta, mean and variance to two consts that represent the same transformation
        a, b = BatchNorm.get_a_b(gamma, beta, mean, variance, epsilon)

        const_inputs_to_add = {
            BatchNorm.Inputs.A: ConstNodeCfg(node.name + '_a', a),
            BatchNorm.Inputs.B: ConstNodeCfg(node.name + '_b', b)
        }

        inputs_to_detach = [1, 2, 3, 4]
        request = GraphRequest(inputs_to_detach=inputs_to_detach,
                               const_inputs_to_insert=const_inputs_to_add)    # type: ignore

        batch_norm_node = BatchNorm(node.name, TORCH_CHANNELS_AXIS)
        return batch_norm_node, request
