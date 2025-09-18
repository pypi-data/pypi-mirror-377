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
Created on 10/13/22

@author: irenab
"""
import abc
import functools
from typing import Union, Optional, Tuple, List

from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.multigraph.node_graph_api import NodeGraphContext, GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.nnir_graph.semantics import DataFormat
from uni.common.core.common import OpInfo, Framework


def validate_onnx(num_inputs: Optional[Union[int, List[int]]],
                  num_outputs: Optional[Union[int, List[int]]],
                  attrs: List,
                  optional_attrs: Optional[List] = None,
                  opset_limits: Optional[Tuple[int, int]] = None):
    """
    Validation decorator for NnirNode onnx factory. The validator refers to the onnx op.

    Args:
        num_inputs: #inputs. If op has optional inputs, a list of possible #inputs. None for non-fixed #inputs.
        num_outputs: #outputs. If op has optional outputs, a list of possible #outputs. None for non-fixed #outputs.
        attrs: expected mandatory attributes.
        optional_attrs: possible optional attributes
        opset_limits: supported opset versions range (inclusive) as tuple (low, high)

    Returns:
    """
    attrs = attrs or []
    optional_attrs = optional_attrs or []

    def decorator(func):

        @functools.wraps(func)
        def decorated(cls, onnx_node, graph_ctx):
            # validate opset matches supported versions
            opset_low, opset_high = opset_limits if opset_limits else (None, None)
            opset = onnx_node.get_opset()
            assert (opset_low is None or opset >= opset_low) and (opset_high is None or opset <= opset_high), \
                f'Supported opsets {opset_limits}, received opset {opset}'

            if num_inputs is not None:
                num_inputs_list = [num_inputs] if isinstance(num_inputs, int) else num_inputs
                deg_in = graph_ctx.get_in_degree()
                assert deg_in in num_inputs_list, \
                    f'Unexpected num inputs for op {onnx_node.op_type}: expected {num_inputs}, actual {deg_in}'
            if num_outputs is not None:
                num_outputs_list = [num_outputs] if isinstance(num_outputs, int) else num_outputs
                deg_out = graph_ctx.get_out_degree()
                assert deg_out in num_outputs_list, \
                    f'Unexpected num outputs for op {onnx_node.op_type}: expected {num_outputs}, actual {deg_out}'

            node_attrs = list(onnx_node.attr.keys())
            missing_attrs = [a for a in attrs if a not in node_attrs]
            assert optional_attrs is not None
            unknown_attrs = [a for a in node_attrs if a not in attrs + optional_attrs]
            if missing_attrs or unknown_attrs:
                raise ValueError(f'Missing or unknown attrs for op {onnx_node.op_type}: '
                                 f'mandatory {attrs}, optional {optional_attrs}, actual {node_attrs}')
            return func(cls, onnx_node, graph_ctx=graph_ctx)

        # mark function as decorated so that it can be validated
        decorated.valid = True    # type: ignore[attr-defined]
        return decorated

    return decorator


class OnnxFactoryBase(abc.ABC):

    data_format = DataFormat.CHW

    @classmethod
    @abc.abstractmethod
    @validate_onnx(num_inputs=1, num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode,
                  graph_ctx: NodeGraphContext) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        """ Creates node instance from OnnxMetaNode """
        raise NotImplementedError()

    @staticmethod
    def onnx_op_info(onnx_node: OnnxMetaNode):
        return OpInfo(node_id=onnx_node.name, op=onnx_node.op_type, framework=Framework.onnx)
