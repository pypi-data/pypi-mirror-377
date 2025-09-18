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
from enum import Enum
from .nnir_node import NnirNode
from uni.common.core.error.util import exceeds_limit_msg, OpInputErrorInfo, raise_op_error
from uni.common.core.nnir_graph.semantics import SemanticsHelper, Semantics

# CBE limits Upsampling is limited to Hin < 4094, Win < 4094.
MAX_UPSAMPLE_IN = 4093


class ResizeMode(Enum):
    BILINEAR = 0
    NEAREST = 1


class Resize(NnirNode):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    invalid_upsampling_h_msg = exceeds_limit_msg("Input height for upsampling", MAX_UPSAMPLE_IN)
    invalid_upsampling_w_msg = exceeds_limit_msg("Input width for upsampling", MAX_UPSAMPLE_IN)

    def __init__(self, name, target_height: int, target_width: int, mode: ResizeMode, **kwargs):
        super().__init__(name, **kwargs)
        self.target_height = target_height
        self.target_width = target_width
        self.mode = mode

    def _validate(self):
        h_index, w_index = self.data_format.get_hw_axes()
        hin = self.graph_ctx.get_in_shapes()[0][h_index]
        win = self.graph_ctx.get_in_shapes()[0][w_index]
        hout, wout = self.target_height, self.target_width
        errors = []
        if hout > hin > MAX_UPSAMPLE_IN:
            errors.append(OpInputErrorInfo(0, 'X', self.invalid_upsampling_h_msg))
        if wout > win > MAX_UPSAMPLE_IN:
            errors.append(OpInputErrorInfo(0, 'X', self.invalid_upsampling_w_msg))
        if errors:
            raise_op_error(self.op_info(), errors, self.history)

    def get_input_semantics(self, semantics_helper: SemanticsHelper) -> Semantics:
        return self.__get_semantics(semantics_helper)

    def set_output_semantics(self, semantics_helper: SemanticsHelper):
        self.output_semantics = self.__get_semantics(semantics_helper)

    @staticmethod
    def __get_semantics(semantics_helper: SemanticsHelper):
        return semantics_helper.node_data_semantics()

    def export_uni_model(self):

        def get_method():
            from uni_model import ResizeMethod
            modes = {
                ResizeMode.BILINEAR: ResizeMethod.BILINEAR,
                ResizeMode.NEAREST: ResizeMethod.NEAREST,
            }
            if self.mode not in modes:
                raise ValueError(f'Invalid ResizeMode: {self.mode}')
            return modes[self.mode]

        from uni_model import UniLayerResize
        return UniLayerResize(self.name,
                              height=self.target_height,
                              width=self.target_width,
                              method=get_method(),
                              data_format=self.get_uni_model_input_data_layout(),
                              out_dtypes=self.get_uni_model_out_dtypes())
