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
from uni_model import PlaceholderDtype
from .nnir_node import NnirNode
from uni.common.core.nnir_graph.semantics import SemanticsHelper


class Placeholder(NnirNode):
    NUM_INPUTS = 0
    NUM_OUTPUTS = 1

    def __init__(self, name, shape, ordinal, data_format, dtype=None, **kwargs):
        super().__init__(name, **kwargs)
        self.shape = shape
        self.ordinal = ordinal
        self.data_format = data_format
        self.dtype = dtype

    def set_output_semantics(self, semantics_helper: SemanticsHelper):
        self.output_semantics = semantics_helper.node_data_semantics()

    def export_uni_model(self):
        from uni_model import UniLayerPlaceholder, shape_of
        if self.shape[0] is None:
            self.shape = (1, ) + self.shape[1:]
        return UniLayerPlaceholder(self.name,
                                   out_shapes=[shape_of(*self.shape)],
                                   ordinal=self.ordinal,
                                   dtype=self._get_dtype(),
                                   data_format=self.get_uni_model_input_data_layout(),
                                   out_dtypes=self.get_uni_model_out_dtypes())

    def _get_dtype(self) -> PlaceholderDtype:
        return PlaceholderDtype.FLOAT32
