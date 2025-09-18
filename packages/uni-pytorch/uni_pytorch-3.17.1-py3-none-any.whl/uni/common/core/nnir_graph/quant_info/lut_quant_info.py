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
from dataclasses import dataclass
from typing import Tuple

import numpy as np

from uni.common.core.nnir_graph.quant_info import QuantInfoBase


@dataclass(frozen=True)
class LUTQuantInfo(QuantInfoBase):
    lut_values: Tuple[float, ...]
    threshold: float
    lut_values_bitwidth: int
    signed: bool

    def __eq__(self, other):
        return ((super().__eq__(other) and np.allclose(self.lut_values, other.lut_values)
                 and np.isclose(self.threshold, other.threshold))
                and self.lut_values_bitwidth == other.lut_values_bitwidth and self.signed == other.signed)

    def export_uni_model(self):
        # in uni-model nbits is the range of quantized values is usually 8
        # and table_n_bits is usually 2/4
        # convert to float for safety reasons
        from uni_model import LutPerTensor, MinMaxOpenEnded
        # for uni-model 2.2.24 value_n_bits and lut_values_bitwidth are switched
        if self.signed:
            threshold_func = MinMaxOpenEnded.from_open_symmetric_threshold
        else:
            threshold_func = MinMaxOpenEnded.from_open_positive_threshold
        return LutPerTensor(value_n_bits=int(self.lut_values_bitwidth),
                            min_max=threshold_func(float(self.threshold)),
                            table=[float(v) for v in self.lut_values],
                            table_n_bits=int(self.value_n_bits),
                            normalized_min=-1 * 2**(self.lut_values_bitwidth - 1),
                            normalized_max=2**(self.lut_values_bitwidth - 1))
