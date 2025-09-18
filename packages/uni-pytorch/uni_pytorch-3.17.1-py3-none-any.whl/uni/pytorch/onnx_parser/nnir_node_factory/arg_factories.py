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
Created on 11/23/23

@author: lotanw
"""
import abc
from typing import Type, Union, Tuple

from uni.common.core.error import raise_op_param_error

from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeToInsertCfg, NodePosition

from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Argmax, Reshape
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import validate_onnx, OnnxFactoryBase


class OnnxArgToNnirNodeBase(OnnxFactoryBase, abc.ABC):
    nnir_op: Type[NnirNode]

    last_index_err_msg: str = "select_last_index is not supported"

    @classmethod
    @validate_onnx(num_inputs=1, num_outputs=1, attrs=[], optional_attrs=['axis', 'keepdims', 'select_last_index'])
    def from_onnx(cls, onnx_node, graph_ctx=None) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        select_last_index = bool(onnx_node.get_attr_with_default_from_schema('select_last_index'))
        if select_last_index:
            raise_op_param_error(cls.onnx_op_info(onnx_node),
                                 param_name='select_last_index',
                                 param_value=select_last_index,
                                 reason=cls.last_index_err_msg,
                                 history=None)
        axis = onnx_node.get_attr_with_default_from_schema('axis')
        keepdims = bool(onnx_node.get_attr_with_default_from_schema('keepdims'))
        if keepdims:
            out_shape = graph_ctx.get_out_shapes()[0]
            reshape = Reshape(
                "arg_reshape",
                out_shape,
                history="when keepdims=True, using reshape after arg_ops to retrieve the missing dimension")
            request = GraphRequest(adjacent_node_to_insert=NodeToInsertCfg(reshape, out_shape, NodePosition.NODE_AFTER))
            return cls.nnir_op(onnx_node.name, axis=axis), request
        return cls.nnir_op(onnx_node.name, axis=axis)


class OnnxArgmaxToNnirNode(OnnxArgToNnirNodeBase):
    """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#ArgMax """
    nnir_op = Argmax
