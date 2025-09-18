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
from typing import List

from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.error import ErrorInfo, ParamErrorInfo, raise_op_error

ONLY_LAST_AXIS = False


class TopKGather(NnirNode):
    NUM_INPUTS = 2
    NUM_OUTPUTS = 1

    input_rank_mismatch = "data and indices tensors are not of the same rank"
    axis_on_batch = "axis is on batch dimension"

    def __init__(self, name, axis, **kwargs):
        super().__init__(name, **kwargs)
        self.axis = axis
        if self.axis is None:
            self.axis = 0

    def export_uni_model(self):
        from uni_model import UniLayerTopKGather
        return UniLayerTopKGather(self.name, axis=self.axis, out_dtypes=self.get_uni_model_out_dtypes())

    def _validate(self):
        in_shapes = self.graph_ctx.get_in_shapes()
        in_nodes: List[NnirNode] = self.graph_ctx.get_in_nodes()
        axis = self.axis
        data_shape, indices_shape = in_shapes[0], in_shapes[1]
        data_node, _ = in_nodes[0], in_nodes[1]
        errors: List[ErrorInfo] = []

        data_shape_without_batch = self._shape_without_batch(data_shape)
        indices_shape_without_batch = self._shape_without_batch(indices_shape)
        if len(data_shape) != len(indices_shape) and len(data_shape_without_batch) != len(indices_shape_without_batch):
            errors.append(ParamErrorInfo("rank mismatch", 0, self.input_rank_mismatch))

        if ONLY_LAST_AXIS:
            axis_err = self.validate_last_index_axis(axis, data_shape, return_error=True)
            if axis_err is not None:
                errors.append(axis_err)
        else:
            if axis == 0 or axis == -len(data_shape):
                if not data_node.is_const():
                    errors.append(ParamErrorInfo("axis", axis, self.axis_on_batch))

        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    @staticmethod
    def _shape_without_batch(shape):
        return [d for d in shape if d is not None]
