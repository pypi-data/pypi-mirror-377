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

from uni.common.core.nnir_graph.quant_info import QuantInfoBase
import numpy as np


@dataclass(frozen=True)
class SymmetricQuantInfo(QuantInfoBase):
    threshold: float
    signed: bool

    def export_uni_model(self):
        from uni_model import QtypePerTensor, MinMaxOpenEnded
        if self.signed:
            min_max = MinMaxOpenEnded.from_open_symmetric_threshold(threshold=float(self.threshold))
        else:
            min_max = MinMaxOpenEnded.from_open_positive_threshold(threshold=float(self.threshold))
        return QtypePerTensor(value_n_bits=int(self.value_n_bits), min_max=min_max)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, SymmetricQuantInfo):
            return False
        return (np.isclose(self.threshold, other.threshold) and self.signed == other.signed
                and self.value_n_bits == other.value_n_bits)
