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
Created on 12/19/22

@author: irenab
"""
from .nnir_node import NnirNode
from uni.common.core.error.util import supported_vals_msg


class Slice(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    supported_batch_slice_size = [NnirNode.batch_size, -1]
    invalid_batch_slice_size_error = 'Invalid size for batch dim. ' + supported_vals_msg(supported_batch_slice_size)

    def __init__(self, name, begin, size, **kwargs):
        super().__init__(name, **kwargs)
        self.begin = begin
        self.size = size
        assert len(self.size) == len(self.begin)

    def _validate(self) -> None:
        self.validate_batch(input_index=0)

        if self.size[0] not in self.supported_batch_slice_size:
            self.raise_op_param_error('size', self.size, self.invalid_batch_slice_size_error)

    def export_uni_model(self):
        from uni_model import UniLayerSlice
        return UniLayerSlice(self.name,
                             begin=[int(v) for v in self.begin],
                             size=[int(v) for v in self.size],
                             out_dtypes=self.get_uni_model_out_dtypes())
