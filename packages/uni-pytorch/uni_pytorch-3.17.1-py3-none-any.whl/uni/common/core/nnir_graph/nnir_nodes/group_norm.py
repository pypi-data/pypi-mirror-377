# -------------------------------------------------------------------------------
# (c) Copyright 2025 Sony Semiconductor Israel, Ltd. All rights reserved.
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

from enum import IntEnum
from uni.common.core.error import raise_op_error
from .nnir_node import NnirNode


class GroupNorm(NnirNode):
    NUM_INPUTS = 3
    NUM_OUTPUTS = 1

    class Inputs(IntEnum):
        Data = 0
        Gamma = 1
        Beta = 2

    max_axis_size = 2**14 - 1

    def __init__(self, name, num_groups: int, epsilon: float, **kwargs):
        super().__init__(name, **kwargs)
        self.num_groups = num_groups
        self.epsilon = epsilon

    def _validate(self):
        errors = []

        err = self.validate_input_dim_size(0, axis_index=1, upper_limit=self.max_axis_size, return_error=True)
        if err:
            errors.append(err)

        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerGroupNorm
        # gamma and beta should always be present.
        return UniLayerGroupNorm(self.name,
                                 num_groups=int(self.num_groups),
                                 epsilon=float(self.epsilon),
                                 out_dtypes=self.get_uni_model_out_dtypes())
