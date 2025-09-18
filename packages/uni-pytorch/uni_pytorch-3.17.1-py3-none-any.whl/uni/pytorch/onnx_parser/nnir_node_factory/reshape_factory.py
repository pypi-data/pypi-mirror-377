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
Created on 10/19/22

@author: irenab
"""
from typing import Tuple, Sequence

from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.nnir_graph.nnir_nodes import Reshape
from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest
from uni.common.core.error.util import raise_op_input_error


class OnnxReshapeToNnirNode(OnnxFactoryBase):

    const_input_index = 1

    zero_in_shape_err_msg = '0 in shape is not supported'

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=1, attrs=[], optional_attrs=['allowzero'])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx: NodeGraphContext) -> Tuple[Reshape, GraphRequest]:
        """ Onnx allows 0 in target shape. 'allowzero' specifies how it is handled.
            See https://github.com/onnx/onnx/blob/main/docs/Operators.md#Reshape
            We don't support 0 in shape
        """
        # https://mypy.readthedocs.io/en/stable/common_issues.html#variance
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        assert len(in_nodes) == 2
        const_input = in_nodes[cls.const_input_index]
        target_shape = tuple(const_input.get_const_data())
        if target_shape[0] == 0:
            # only in case of reshape -> InstanceNormalization allow 0 in the first dimension
            # replace the 0 to 1 to avoid validation error
            # see InstanceNormSubstitution
            out_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_out_nodes()    # type: ignore
            if (len(out_nodes) == 1 and len(out_nodes[0]) == 1 and    # type: ignore
                    out_nodes[0][0].op_type == 'InstanceNormalization'):    # type: ignore
                target_shape = (1, *target_shape[1:])
        if 0 in target_shape:
            raise_op_input_error(cls.onnx_op_info(onnx_node),
                                 input_index=cls.const_input_index,
                                 input_name=const_input.name,
                                 reason=cls.zero_in_shape_err_msg,
                                 history=None)

        node = Reshape(onnx_node.name, target_shape)
        return node, GraphRequest(inputs_to_detach=[cls.const_input_index])
