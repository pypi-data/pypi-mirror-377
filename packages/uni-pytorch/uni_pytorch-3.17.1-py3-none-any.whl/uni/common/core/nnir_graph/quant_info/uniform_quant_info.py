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
Created on 8/6/22

@author: irenab
"""

from dataclasses import dataclass
import numpy as np

from uni.common.core.nnir_graph.quant_info import QuantInfoBase


@dataclass(frozen=True)
class UniformQuantInfo(QuantInfoBase):
    min_val: float
    max_val: float

    def export_uni_model(self):
        from uni_model import QtypePerTensor, MinMaxOpenEnded
        min_max = MinMaxOpenEnded(min=float(self.min_val), max=float(self.max_val))
        return QtypePerTensor(value_n_bits=int(self.value_n_bits), min_max=min_max)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, UniformQuantInfo):
            return False
        return (np.isclose(self.min_val, other.min_val) and np.isclose(self.max_val, other.max_val)
                and self.value_n_bits == other.value_n_bits)
