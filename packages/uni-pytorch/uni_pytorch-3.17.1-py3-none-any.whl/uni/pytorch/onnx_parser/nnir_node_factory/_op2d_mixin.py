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
import abc
from typing import Tuple, List, Optional, Union

from uni.common.core.error.defs import ParamErrorInfo, OpInputErrorInfo
from uni.common.core.error.util import supported_vals_msg, raise_op_error
from uni.common.core.multigraph.node_graph_api import NodeGraphContext
from uni.common.core.nnir_graph.nnir_nodes.common import Padding2d
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase


class OnnxOp2dMixin(abc.ABC):
    supported_autopad = ['NOTSET', 'VALID']
    error_ambiguous_pad = 'Conflicting auto_pad and pads'
    error_unsupported_pad = supported_vals_msg(supported_autopad)

    @classmethod
    def read_and_validate_pad(cls,
                              onnx_node,
                              return_error: bool = False) -> Tuple[Optional[Padding2d], List[ParamErrorInfo]]:
        """
            validates pads,
            checks if node's autopad is in supported_autopad, derived classes can override supported_autopad
            checks that there are no explicit pads for anything other than NOTSET
            SAME padding should be calculated individually
        """

        errs = []
        auto_pad = onnx_node.get_attr_with_default_from_schema('auto_pad')

        if auto_pad not in cls.supported_autopad:
            errs.append(ParamErrorInfo(name='auto_pad', value=auto_pad, reason=cls.error_unsupported_pad))

        # the order is d1_begin, d2_begin,.. dn_begin, d1_end, d2_end,.. dn_end
        pad = onnx_node.get_attr_with_default('pads', (0, 0, 0, 0))
        pad2d: Union[Padding2d, None] = Padding2d(h=(pad[0], pad[2]), w=(pad[1], pad[3]))

        if auto_pad != 'NOTSET' and pad2d != Padding2d():
            errs.append(ParamErrorInfo(name='auto_pad', value=auto_pad, reason=cls.error_ambiguous_pad))
            errs.append(ParamErrorInfo(name='pads', value=pad, reason=cls.error_ambiguous_pad))

        # other autopads must calculate padding differently, no reason to send back miscalculated pad values
        if auto_pad not in ['NOTSET', 'VALID']:
            pad2d = None

        if return_error is False and errs:
            raise_op_error(OnnxFactoryBase.onnx_op_info(onnx_node), errors=errs, history=None)

        return pad2d, errs

    @staticmethod
    def op2d_input_dim_error_msg(ndims):
        return f'Only 2d Op is supported. Expected 4d input NxCxHxW, actual {ndims}d'

    @classmethod
    def validate_2d_op_data_shape(cls,
                                  onnx_node: OnnxMetaNode,
                                  graph_ctx: NodeGraphContext,
                                  input_index: int = 0,
                                  return_error: bool = False) -> Optional[OpInputErrorInfo]:
        """ Validates that data input for the  2d op is 4d (onnx doesn't have designated 2d ops)
            graph_ctx: node's graph_ctx
            input_index: index of the input tensor to validate. By default, 0.
            return_error: whether to return error object (so that it can be aggregated with other errors)
                          or raise an error. By default, raises an error."""
        input_shapes = graph_ctx.get_in_shapes()
        ndims = len(input_shapes[0])
        if ndims == 4:
            return None

        node_in: OnnxMetaNode = graph_ctx.get_in_nodes()[0]
        err = OpInputErrorInfo(input_index=input_index,
                               input_name=node_in.name,
                               reason=cls.op2d_input_dim_error_msg(ndims))
        if return_error is False:
            raise_op_error(OnnxFactoryBase.onnx_op_info(onnx_node), errors=[err], history=None)

        return err
