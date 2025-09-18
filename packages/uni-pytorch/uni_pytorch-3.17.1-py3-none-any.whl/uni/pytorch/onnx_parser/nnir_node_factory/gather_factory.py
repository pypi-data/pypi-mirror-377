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
"""
Created on 4/16/24

@author: irenab
"""
from typing import Tuple, List

import numpy as np

from uni.common.core.error import OpInputErrorInfo, ParamErrorInfo, raise_op_error, ErrorInfo
from uni.common.core.multigraph.node_graph_api import GraphRequest, NodeToInsertCfg, NodePosition
from uni.common.core.nnir_graph.nnir_nodes import StridedSlice, Squeeze
from uni.common.core.node_history import NodeHistory
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx


class OnnxGatherToNnirNode(OnnxFactoryBase):

    indices_error = 'Gather is supported only for a single index'
    dynamic_indices_error = 'Gather dynamic indices are not supported'
    invalid_axis_error = 'Gather along batch axis is not supported'

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=1, attrs=[], optional_attrs=['axis'])
    def from_onnx(cls, onnx_node, graph_ctx=None) -> Tuple[StridedSlice, GraphRequest]:
        axis = onnx_node.get_attr_with_default_from_schema('axis')
        input_shape = graph_ctx.get_in_shapes()[0]
        errs: List[ErrorInfo] = []
        if axis in [0, -len(input_shape)]:
            errs.append(ParamErrorInfo(name='axis', value=axis, reason=cls.invalid_axis_error))

        _, ind_node = graph_ctx.get_in_nodes()
        if ind_node.is_const(check_quant=False) is False:
            errs.append(OpInputErrorInfo(input_index=1, input_name='indices', reason=cls.dynamic_indices_error))
            raise_op_error(cls.onnx_op_info(onnx_node), errs, None)
        indices = ind_node.get_const_data()
        if indices.size != 1:
            errs.append(OpInputErrorInfo(input_index=1, input_name='indices', reason=cls.indices_error))

        if errs:
            raise_op_error(cls.onnx_op_info(onnx_node), errs, None)

        index = indices.item()
        begin = [0] * len(input_shape)
        end = [0] * len(input_shape)
        begin[axis] = index
        end[axis] = index + 1
        strides = list(np.ones_like(input_shape))
        # set end mask for all axes except axis. if index=-1, set end mask as well, otherwise end becomes 0
        end_mask_axes = [i for i in range(len(input_shape)) if i != axis or begin[axis] == -1]
        end_mask = StridedSlice.calculate_mask(end_mask_axes)
        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='Gather (select) -> Slice, Squeeze')

        slice_node = StridedSlice(name=onnx_node.name,
                                  begin=begin,
                                  end=end,
                                  begin_mask=0,
                                  end_mask=end_mask,
                                  strides=strides,
                                  history=history)

        squeeze_node = Squeeze(onnx_node.name + '_squeeze', squeeze_dims=[axis])
        request = GraphRequest(inputs_to_detach=[1],
                               adjacent_node_to_insert=NodeToInsertCfg(squeeze_node, input_shape,
                                                                       NodePosition.NODE_AFTER))

        return slice_node, request
