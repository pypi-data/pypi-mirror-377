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
Created on 3/20/23

@author: irenab
"""
from typing import Union, Sequence

from .nnir_node import NnirNode


class Split(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = None

    def __init__(self, name: str, axis: int, num_splits_or_sizes: Union[int, Sequence[int]], **kwargs):
        self.axis = axis
        self.num_splits = None
        self.split_sizes = None
        if isinstance(num_splits_or_sizes, int):
            self.num_splits = num_splits_or_sizes
        else:
            self.split_sizes = tuple(num_splits_or_sizes)
        # super().__init__ call to get_uni_model_num_outputs so is needs to be after setting the num_splits/split_sizes
        super().__init__(name, **kwargs)

    def _validate(self):
        self.validate_batch(input_index=0)

        self.validate_non_batch_op_axis(self.axis)

    def get_uni_model_num_outputs(self):
        assert self.num_splits is not None or self.split_sizes is not None
        return self.num_splits if self.num_splits else len(self.split_sizes)    # type: ignore

    def export_uni_model(self):
        if self.num_splits:
            assert self.split_sizes is None
            from uni_model import UniLayerSplit
            return UniLayerSplit(self.name,
                                 num_split=self.num_splits,
                                 split_dim=self.axis,
                                 out_dtypes=self.get_uni_model_out_dtypes())
        else:
            assert self.split_sizes and self.num_splits is None
            from uni_model import UniLayerSplitV
            return UniLayerSplitV(self.name,
                                  split_sizes=list(self.split_sizes),
                                  split_dim=self.axis,
                                  out_dtypes=self.get_uni_model_out_dtypes())
