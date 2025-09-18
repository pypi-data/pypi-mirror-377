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
Created on 1/1/23

@author: irenab
"""
from typing import Union, Sequence

from uni.common.core.error import raise_op_param_error
from .nnir_node import NnirNode


class Softmax(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    last_dim_max_size = 2**15 - 1    # 32k
    unsupported_axis_error = 'Only single axis is supported'

    def __init__(self, name, axis: Union[int, Sequence], **kwargs):
        super().__init__(name, **kwargs)
        self.axes = [axis] if isinstance(axis, int) else list(axis)

    def _validate(self):
        self.validate_batch()
        if len(self.axes) != 1:
            raise_op_param_error(self.op_info(), 'axes', self.axes, self.unsupported_axis_error, self.history)
        self.validate_non_batch_op_axis(self.axes[0])

        self.validate_input_dim_size(input_index=0, axis_index=self.axes[0], upper_limit=self.last_dim_max_size)

    def export_uni_model(self):
        from uni_model import UniLayerSoftmax
        return UniLayerSoftmax(self.name, axis=self.axes[0], out_dtypes=self.get_uni_model_out_dtypes())
