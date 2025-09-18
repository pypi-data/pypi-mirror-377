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
Created on 8/4/22

@author: irenab
"""
import numpy as np
from uni_model import create_const_with_data

from .nnir_node import NnirNode


class Variable(NnirNode):
    NUM_INPUTS = 0
    NUM_OUTPUTS = 1

    def __init__(self, name, data: np.ndarray, quant_info, **kwargs):
        super().__init__(name, **kwargs)
        assert isinstance(data, (np.number, np.ndarray))
        if not data.shape:
            data = data.reshape(1)
        self.data = data
        self.shape = data.shape
        if quant_info is not None:
            self.set_quant(quant_info, 0)

    def export_uni_model(self):
        # TODO change this to use from uni_model.uni_const_from_numpy when they support layouts
        return create_const_with_data(self.name, self.data.astype(np.float32), dtype=self.get_uni_model_out_dtypes()[0])
