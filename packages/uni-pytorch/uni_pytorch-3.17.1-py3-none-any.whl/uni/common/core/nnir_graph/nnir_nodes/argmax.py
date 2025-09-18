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
Created on 9/27/23

@author: lotanw
"""
from typing import List

from uni.common.core.error import ErrorInfo, OpInputErrorInfo, raise_op_error
from uni.common.core.nnir_graph.nnir_nodes import NnirNode


class Argmax(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    MAX_AXIS_DIM_SIZE = 2**14
    axis_dim_size_err_msg = "Size of reduced axis must not exceed 16K."

    def __init__(self, name, axis: int, **kwargs):
        super().__init__(name, **kwargs)
        self.axis = axis

    def _validate(self):
        self.validate_non_batch_op_axis(self.axis)
        data_shape = self.graph_ctx.get_in_shapes()[0]
        errors: List[ErrorInfo] = []
        if data_shape[self.axis] >= self.MAX_AXIS_DIM_SIZE:
            errors.append(OpInputErrorInfo(input_index=0, input_name="input", reason=self.axis_dim_size_err_msg))

        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerArgMax
        return UniLayerArgMax(self.name, axis=self.axis, out_dtypes=self.get_uni_model_out_dtypes())
