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
from typing import Tuple, Sequence

from uni.common.core.error import OpInputErrorInfo, raise_op_error
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxMetaNode
from uni.common.core.node_history import NodeHistory
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import StridedSlice


class OnnxSliceToNnirNode(OnnxFactoryBase):

    @staticmethod
    def get_dynamic_indices_error(name):
        return f'Slice dynamic {name} are not supported'

    @classmethod
    @validate_onnx(num_inputs=[3, 4, 5], num_outputs=1, attrs=[])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx=None) -> Tuple[StridedSlice, GraphRequest]:
        """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#Slice """
        from uni.pytorch.onnx_parser.onnx_parser import is_dummy_input
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        data_shape = graph_ctx.get_in_shapes()[0]
        errs = []
        for i in range(1, len(in_nodes)):
            if in_nodes[i].is_const(check_quant=False) is False:
                if i in [3, 4] and is_dummy_input(in_nodes[i]):
                    continue
                input_names = {1: 'starts', 2: 'ends', 3: 'axes', 4: 'steps'}
                errs.append(
                    OpInputErrorInfo(input_index=i,
                                     input_name=input_names[i],
                                     reason=cls.get_dynamic_indices_error(input_names[i])))
        if errs:
            raise_op_error(cls.onnx_op_info(onnx_node), errs, None)

        starts = in_nodes[1].get_const_data()
        ends = in_nodes[2].get_const_data()
        axes, steps = None, None

        if len(in_nodes) > 3 and not is_dummy_input(in_nodes[3]):
            axes = list(in_nodes[3].get_const_data())
        if len(in_nodes) > 4 and not is_dummy_input(in_nodes[4]):
            steps = list(in_nodes[4].get_const_data())

        history = NodeHistory(cls.onnx_op_info(onnx_node), desc='')
        req = GraphRequest(inputs_to_detach=list(range(len(in_nodes)))[1:])

        data_rank = len(graph_ctx.get_in_shapes()[0])
        # init default values
        if axes is None:
            axes = list(range(data_rank))
        if steps is None:
            steps = [1] * len(axes)

        # make axes positive
        axes = [data_rank + i if i < 0 else i for i in axes]

        assert len(starts) == len(ends) == len(axes) == len(steps)
        assert len(axes) == len(set(axes)), "axes must be unique"
        assert all([s != 0 for s in steps])

        begin, end, strides = [0] * data_rank, [0] * data_rank, [1] * data_rank
        for i in axes:
            begin[i] = starts[axes.index(i)]
            end[i] = ends[axes.index(i)]
            # if slice does not have stop in torch ([x:]), end will have sys.maxsize
            if data_shape and data_shape[i] is not None:
                end[i] = min(data_shape[i], end[i])
            strides[i] = steps[axes.index(i)]

        masked_axes = [i for i in range(data_rank) if i not in axes]
        mask = StridedSlice.calculate_mask(masked_axes)

        return StridedSlice(onnx_node.name,
                            begin=begin,
                            end=end,
                            strides=strides,
                            begin_mask=mask,
                            end_mask=mask,
                            history=history), req
