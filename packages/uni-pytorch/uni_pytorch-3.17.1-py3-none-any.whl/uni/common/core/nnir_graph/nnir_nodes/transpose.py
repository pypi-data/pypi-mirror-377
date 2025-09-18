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
Created on 1/5/23

@author: irenab
"""
from typing import List

from uni.common.core.error import ParamErrorInfo, raise_op_error, ErrorInfo
from .nnir_node import NnirNode


class Transpose(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    batch_permute_error = 'Batch axis must remain the first axis'

    def __init__(self, name, axes: tuple, **kwargs):
        super().__init__(name, **kwargs)
        # incl batch
        self.axes = axes

    def _validate(self):
        if len(self.graph_ctx.get_in_shapes()[0]) != len(self.axes):
            raise RuntimeError('Mismatch between num axes and num input dims')

        errors: List[ErrorInfo] = []
        err = self.validate_batch(input_index=0, return_error=True)
        if err:
            errors.append(err)
        if self.axes[0] != 0:
            errors.append(ParamErrorInfo(name='axes', value=self.axes, reason=self.batch_permute_error))
        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerTranspose
        return UniLayerTranspose(self.name,
                                 axis_select=[int(v) for v in self.axes],
                                 out_dtypes=self.get_uni_model_out_dtypes())
