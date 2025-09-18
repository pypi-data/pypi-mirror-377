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
from typing import Tuple, Optional, Sequence, List

import numpy as np

from uni.common.core.error import OpOutputErrorInfo, raise_op_error, ErrorInfo

from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest, ConstNodeCfg

from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.nnir_graph.nnir_nodes import LayerNorm


class OnnxLayerNormToNnirNode(OnnxFactoryBase):
    """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#LayerNormalization """
    only_one_out_err_msg = ("Only the normalized data output of the ONNX node is supported."
                            " Other outputs should not be used")

    @classmethod
    @validate_onnx(num_inputs=[2, 3], num_outputs=[1, 2, 3], attrs=[], optional_attrs=['axis', 'epsilon', 'stash_type'])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> \
            Tuple[LayerNorm, Optional[GraphRequest]]:
        axis = onnx_node.get_attr_with_default_from_schema('axis')
        epsilon = onnx_node.get_attr_with_default_from_schema('epsilon')
        cls._check_errors(graph_ctx, onnx_node)
        request = None
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        if len(in_nodes) == 2 or in_nodes[2].is_dummy_input():
            beta_size = graph_ctx.get_in_shapes()[1][-1]
            beta = np.array([0.] * beta_size, dtype=np.float32)
            const_inputs_to_add = {LayerNorm.Inputs.Beta.value: ConstNodeCfg(onnx_node.name + '_beta', beta)}
            inputs_to_detach = [2] if len(in_nodes) == 3 else []
            request = GraphRequest(inputs_to_detach=inputs_to_detach, const_inputs_to_insert=const_inputs_to_add)

        return LayerNorm(onnx_node.name, axes=axis, epsilon=epsilon), request

    @classmethod
    def _check_errors(cls, graph_ctx, onnx_node):
        errors: List[ErrorInfo] = []
        out_nodes = graph_ctx.get_out_nodes()

        for i, output_name in zip((1, 2), ("Mean", "InvStdDev")):
            if i in out_nodes and not out_nodes[i][0].is_dummy_output():
                errors.append(
                    OpOutputErrorInfo(output_index=i, output_name=output_name, reason=cls.only_one_out_err_msg))
        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)
